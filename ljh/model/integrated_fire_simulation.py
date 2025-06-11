"""
통합 화재 시뮬레이션 시스템
Anderson13 연료모델, 기상 데이터, 지형 효과, 고급 CA 규칙을 모두 통합
"""

import argparse
import numpy as np
import geopandas as gpd
from pathlib import Path
import json
from datetime import datetime
import matplotlib.pyplot as plt
from typing import Optional, Dict, List

# 로컬 모듈 임포트
from advanced_ca_model import AdvancedCAModel
from weather_integration import IntegratedWeatherModel
from terrain_model import TerrainModel
from ca_analyzer import CAAnalyzer

class IntegratedFireSimulation:
    """통합 화재 시뮬레이션 시스템"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        config_path: 설정 파일 경로 (JSON)
        """
        self.config = self.load_config(config_path)
        
        # 컴포넌트 초기화
        self.ca_model = None
        self.weather_model = None
        self.terrain_model = None
        self.analyzer = None
        
        # 데이터
        self.fuel_map = None
        self.fuel_code_map = None
        self.gdf = None
        
        # 결과 저장
        self.results_dir = Path(self.config['output']['results_dir'])
        self.results_dir.mkdir(exist_ok=True)
        
    def load_config(self, config_path: Optional[str] = None) -> Dict:
        """설정 파일 로드"""
        default_config = {
            'input': {
                'shapefile_path': 'model/44200/44200.shp',
                'dem_path': None,
                'weather_api_key': None
            },
            'simulation': {
                'grid_shape': [100, 100],
                'steps': 100,
                'neighborhood': 'moore',
                'seed': 42
            },
            'fire': {
                'ignition_points': [[50, 50]],
                'tree_density': 0.7,
                'base_spread_prob': 0.15,
                'ignition_prob': 0.001,
                'extinguish_prob': 0.05
            },
            'terrain': {
                'use_terrain': True,
                'resolution': 30
            },
            'weather': {
                'use_weather': True,
                'location': [37.5665, 126.9780],  # 서울
                'update_interval': 10
            },
            'suppression': {
                'enabled': False,
                'events': []
            },
            'output': {
                'results_dir': 'integrated_results',
                'save_interval': 10,
                'create_animation': True,
                'create_analysis': True
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            # 기본 설정에 사용자 설정 병합
            default_config.update(user_config)
        
        return default_config
    
    def load_fuel_data(self):
        """연료 데이터 로드 및 처리"""
        print("연료 데이터 로드 중...")
        
        shp_path = self.config['input']['shapefile_path']
        if not Path(shp_path).exists():
            raise FileNotFoundError(f"Shapefile not found: {shp_path}")
        
        # Shapefile 로드 및 Anderson13 매핑
        self.gdf = gpd.read_file(shp_path)
        self.gdf['STORUNST_CD'] = self.gdf['STORUNST_CD'].astype(str).str.zfill(1)
        self.gdf['HEIGT_CD'] = self.gdf['HEIGT_CD'].astype(str).str.zfill(2)
        
        # Anderson13 연료모델 매핑
        conds = [
            (self.gdf['STORUNST_CD'].isin(['0','2'])) | (self.gdf['FRTP_CD']=='0'),
            (self.gdf['STORUNST_CD']=='1') & (self.gdf['FRTP_CD']=='1') & (self.gdf['DNST_CD']=='C') & (self.gdf['HEIGT_CD'].astype(int) >= 20),
            (self.gdf['STORUNST_CD']=='1') & (self.gdf['FRTP_CD']=='1') & (self.gdf['DNST_CD'].isin(['B','C'])),
            (self.gdf['STORUNST_CD']=='1') & (self.gdf['FRTP_CD']=='1'),
            (self.gdf['STORUNST_CD']=='1') & (self.gdf['FRTP_CD']=='2') & (self.gdf['DNST_CD']=='C') & (self.gdf['HEIGT_CD'].astype(int) >= 20),
            (self.gdf['STORUNST_CD']=='1') & (self.gdf['FRTP_CD']=='2') & (self.gdf['DNST_CD'].isin(['B','C'])),
            (self.gdf['STORUNST_CD']=='1') & (self.gdf['FRTP_CD']=='2'),
            (self.gdf['STORUNST_CD']=='1') & (self.gdf['FRTP_CD']=='3') & (self.gdf['DNST_CD']=='C'),
            (self.gdf['STORUNST_CD']=='1') & (self.gdf['FRTP_CD']=='3'),
            (self.gdf['STORUNST_CD']=='1') & (self.gdf['FRTP_CD']=='4'),
            (self.gdf['KOFTR_GROU_CD']=='92'),
            (self.gdf['KOFTR_GROU_CD']=='83'),
            (self.gdf['KOFTR_GROU_CD'].isin(['91','93','94','95','99'])),
        ]
        choices = [
            'NB1', 'TU1', 'TU2', 'TL1', 'TU3', 'TU4', 'TL2', 'TU5', 'TL3', 'GS1', 'GR1', 'SH1', 'NB1'
        ]
        self.gdf['Anderson13_FuelModel'] = np.select(conds, choices, default='TL1')
        
        # 래스터화를 위한 가상 연료맵 생성 (실제로는 rasterio.features.rasterize 사용)
        grid_shape = tuple(self.config['simulation']['grid_shape'])
        
        # 간단한 연료맵 생성 (실제 구현에서는 실제 래스터화 필요)
        self.fuel_code_map = np.random.choice(
            ['TL1', 'TL2', 'TU1', 'TU2', 'GR1', 'NB1'], 
            size=grid_shape, 
            p=[0.3, 0.2, 0.2, 0.15, 0.1, 0.05]
        )
        
        print(f"연료 데이터 로드 완료: {self.gdf.shape[0]} 폴리곤")
    
    def initialize_components(self):
        """모든 컴포넌트 초기화"""
        print("컴포넌트 초기화 중...")
        
        grid_shape = tuple(self.config['simulation']['grid_shape'])
        
        # CA 모델 초기화
        self.ca_model = AdvancedCAModel(
            grid_shape=grid_shape,
            neighborhood=self.config['simulation']['neighborhood'],
            seed=self.config['simulation']['seed']
        )
        
        # 연료맵 설정
        self.ca_model.fuel_map = self.fuel_code_map
        
        # 파라미터 업데이트
        self.ca_model.params.update({
            'base_spread_prob': self.config['fire']['base_spread_prob'],
            'ignition_prob': self.config['fire']['ignition_prob'],
            'extinguish_prob': self.config['fire']['extinguish_prob']
        })
        
        # 지형 모델 초기화
        if self.config['terrain']['use_terrain']:
            dem_path = self.config['input'].get('dem_path')
            self.terrain_model = TerrainModel(
                dem_path=dem_path,
                resolution=self.config['terrain']['resolution']
            )
            self.ca_model.terrain_model = self.terrain_model
        
        # 기상 모델 초기화
        if self.config['weather']['use_weather']:
            api_key = self.config['input'].get('weather_api_key')
            self.weather_model = IntegratedWeatherModel(api_key=api_key)
            self.ca_model.weather_model = self.weather_model
        
        # 분석기 초기화
        self.analyzer = CAAnalyzer(self.results_dir)
        
        print("컴포넌트 초기화 완료")
    
    def setup_initial_conditions(self):
        """초기 조건 설정"""
        print("초기 조건 설정 중...")
        
        # 격자 초기화
        tree_density = self.config['fire']['tree_density']
        firebreaks = self.config.get('firebreaks', [])
        
        self.ca_model.initialize(
            tree_density=tree_density,
            firebreaks=firebreaks
        )
        
        # 점화점 설정
        for ignition_point in self.config['fire']['ignition_points']:
            x, y = ignition_point[:2]
            intensity = ignition_point[2] if len(ignition_point) > 2 else 1.0
            self.ca_model.add_ignition_point(x, y, intensity)
        
        print(f"점화점 {len(self.config['fire']['ignition_points'])}개 설정 완료")
    
    def run_simulation(self):
        """시뮬레이션 실행"""
        print("시뮬레이션 시작...")
        
        steps = self.config['simulation']['steps']
        save_interval = self.config['output']['save_interval']
        weather_update_interval = self.config['weather'].get('update_interval', 10)
        
        # 기상 데이터 초기 수집
        if self.weather_model:
            lat, lon = self.config['weather']['location']
            weather_data = self.weather_model.get_comprehensive_fire_risk(lat, lon)
            print(f"초기 화재 위험도: {weather_data['risk_score']:.3f}")
        
        for step in range(steps):
            # 기상 데이터 업데이트
            if (self.weather_model and 
                step % weather_update_interval == 0 and 
                step > 0):
                
                lat, lon = self.config['weather']['location']
                weather_data = self.weather_model.get_comprehensive_fire_risk(lat, lon)
                
                # 기상 조건에 따른 파라미터 조정
                risk_score = weather_data['risk_score']
                self.ca_model.params['base_spread_prob'] = (
                    self.config['fire']['base_spread_prob'] * (1 + risk_score)
                )
            
            # 소화 활동 적용
            suppression_events = self.config['suppression'].get('events', [])
            for event in suppression_events:
                if event['step'] == step:
                    self.ca_model.apply_suppression(
                        center=tuple(event['center']),
                        radius=event['radius'],
                        effectiveness=event['effectiveness']
                    )
                    print(f"Step {step}: 소화 활동 적용 at {event['center']}")
            
            # 시뮬레이션 스텝 실행
            stats = self.ca_model.step()
            
            # 결과 저장
            if step % save_interval == 0 or step == steps - 1:
                # 격자 상태 저장
                np.save(self.results_dir / f'step_{step:03d}.npy', self.ca_model.grid)
                
                # 이미지 저장
                fig, ax = plt.subplots(figsize=(10, 8))
                colors = ['white', 'green', 'red', 'black', 'blue']
                cmap = plt.matplotlib.colors.ListedColormap(colors)
                
                im = ax.imshow(self.ca_model.grid, cmap=cmap, vmin=0, vmax=4)
                ax.set_title(f'통합 화재 시뮬레이션 - Step {step}')
                ax.axis('off')
                
                # 범례
                legend_elements = [
                    plt.Rectangle((0,0),1,1, facecolor='white', edgecolor='black', label='빈공간'),
                    plt.Rectangle((0,0),1,1, facecolor='green', label='나무'),
                    plt.Rectangle((0,0),1,1, facecolor='red', label='화재'),
                    plt.Rectangle((0,0),1,1, facecolor='black', label='연소후'),
                    plt.Rectangle((0,0),1,1, facecolor='blue', label='습함')
                ]
                ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
                
                plt.tight_layout()
                plt.savefig(self.results_dir / f'step_{step:03d}.png', 
                            dpi=150, bbox_inches='tight')
                plt.close()
            
            # 진행 상황 출력
            if step % 10 == 0:
                burning_cells = stats['burning_cells']
                burned_ratio = stats['burn_ratio'] * 100
                print(f"Step {step:3d}: 활성화재 {burning_cells:4d}셀, "
                      f"연소율 {burned_ratio:5.1f}%")
            
            # 시뮬레이션 완료 체크
            if self.ca_model.is_simulation_complete():
                print(f"시뮬레이션 완료: {step} 스텝에서 화재 진화")
                break
        
        print("시뮬레이션 종료")
    
    def create_analysis(self):
        """분석 및 보고서 생성"""
        if not self.config['output']['create_analysis']:
            return
        
        print("분석 보고서 생성 중...")
        
        # 기본 분석
        df = self.analyzer.analyze_all_steps()
        
        # 시각화 생성
        self.analyzer.plot_fire_progression(
            save_path=self.results_dir / 'fire_progression.png'
        )
        
        self.analyzer.plot_advanced_analysis(
            save_path=self.results_dir / 'advanced_analysis.png'
        )
        
        # 연료 분포 시각화
        if self.fuel_code_map is not None:
            self.analyzer.plot_fuel_distribution(
                fuel_map=self.fuel_code_map,
                save_path=self.results_dir / 'fuel_distribution.png'
            )
        
        # 애니메이션 생성
        if self.config['output']['create_animation']:
            self.analyzer.create_animation(
                output_path=self.results_dir / 'fire_animation.mp4'
            )
        
        # 분석 데이터 내보내기
        self.analyzer.export_analysis_data(
            output_path=self.results_dir / 'analysis_data'
        )
        
        # 보고서 저장
        summary = self.analyzer.save_analysis_report(
            report_path=self.results_dir / 'simulation_report.json'
        )
        
        print("분석 완료!")
        print(f"최종 연소율: {summary['final_burn_ratio']:.2%}")
        print(f"최대 화재 강도: {summary['peak_fire_intensity']:,} 셀")
    
    def save_configuration(self):
        """사용된 설정 저장"""
        config_path = self.results_dir / 'simulation_config.json'
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        print(f"설정 파일 저장: {config_path}")
    
    def run_complete_simulation(self):
        """전체 시뮬레이션 파이프라인 실행"""
        print("=" * 60)
        print("통합 화재 시뮬레이션 시스템")
        print("=" * 60)
        
        try:
            # 1. 데이터 로드
            self.load_fuel_data()
            
            # 2. 컴포넌트 초기화
            self.initialize_components()
            
            # 3. 초기 조건 설정
            self.setup_initial_conditions()
            
            # 4. 시뮬레이션 실행
            start_time = datetime.now()
            self.run_simulation()
            end_time = datetime.now()
            
            # 5. 분석 및 보고서 생성
            self.create_analysis()
            
            # 6. 설정 저장
            self.save_configuration()
            
            # 실행 시간 출력
            execution_time = (end_time - start_time).total_seconds()
            print(f"\n총 실행 시간: {execution_time:.1f}초")
            print(f"결과 저장 위치: {self.results_dir.absolute()}")
            
        except Exception as e:
            print(f"시뮬레이션 실행 중 오류: {e}")
            raise

def create_sample_config():
    """샘플 설정 파일 생성"""
    config = {
        "input": {
            "shapefile_path": "model/44200/44200.shp",
            "dem_path": None,
            "weather_api_key": None
        },
        "simulation": {
            "grid_shape": [150, 150],
            "steps": 200,
            "neighborhood": "moore",
            "seed": 42
        },
        "fire": {
            "ignition_points": [[75, 75, 1.5], [100, 50, 1.2]],
            "tree_density": 0.75,
            "base_spread_prob": 0.12,
            "ignition_prob": 0.0008,
            "extinguish_prob": 0.03
        },
        "firebreaks": [
            {"start": [20, 0], "end": [20, 149], "width": 3},
            {"start": [0, 80], "end": [149, 80], "width": 2}
        ],
        "terrain": {
            "use_terrain": True,
            "resolution": 30
        },
        "weather": {
            "use_weather": True,
            "location": [37.5665, 126.9780],
            "update_interval": 15
        },
        "suppression": {
            "enabled": True,
            "events": [
                {"step": 50, "center": [80, 80], "radius": 8, "effectiveness": 0.85},
                {"step": 100, "center": [105, 55], "radius": 6, "effectiveness": 0.75}
            ]
        },
        "output": {
            "results_dir": "integrated_simulation_results",
            "save_interval": 5,
            "create_animation": True,
            "create_analysis": True
        }
    }
    
    with open('simulation_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("샘플 설정 파일 생성: simulation_config.json")

def main():
    parser = argparse.ArgumentParser(description='통합 화재 시뮬레이션 시스템')
    parser.add_argument('--config', type=str, help='설정 파일 경로')
    parser.add_argument('--create-config', action='store_true', 
                        help='샘플 설정 파일 생성')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
        return
    
    # 시뮬레이션 실행
    simulator = IntegratedFireSimulation(config_path=args.config)
    simulator.run_complete_simulation()

if __name__ == '__main__':
    main()
