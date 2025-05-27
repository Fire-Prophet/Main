"""
통합 검증 및 현실성 시스템
- 모델 검증과 현실성 향상 기능을 통합
- 전체 시뮬레이션 파이프라인에 검증 단계 추가
- 실시간 현실성 모니터링
- 자동화된 모델 개선 제안
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# 로컬 모듈 임포트
try:
    from model_validation import ModelValidator, load_simulation_results, create_synthetic_actual_data
    from realistic_fire_model import RealisticFireModel, DetailedWeatherConditions, HumanActivity
    from advanced_ca_model import AdvancedCAFireModel
    from weather_integration import IntegratedWeatherModel
    from terrain_model import TopographicFireModel
except ImportError as e:
    print(f"모듈 임포트 오류: {e}")
    print("필요한 모든 모듈이 같은 디렉토리에 있는지 확인하세요.")

class IntegratedValidationSystem:
    """통합 검증 및 현실성 시스템"""
    
    def __init__(self, config_path: str = None):
        """
        Args:
            config_path: 설정 파일 경로
        """
        self.config = self._load_config(config_path)
        
        # 모델 컴포넌트들
        self.ca_model = None
        self.realistic_model = None
        self.weather_model = None
        self.terrain_model = None
        self.validator = None
        
        # 결과 저장
        self.simulation_results = {}
        self.validation_results = {}
        self.realism_metrics = {}
        
        # 모니터링 데이터
        self.performance_history = []
        self.improvement_suggestions = []
        
    def _load_config(self, config_path: str) -> Dict:
        """설정 파일 로드"""
        default_config = {
            'simulation': {
                'grid_size': [100, 100],
                'cell_size': 30.0,
                'max_steps': 100,
                'validation_interval': 10
            },
            'validation': {
                'enable_pattern_validation': True,
                'enable_temporal_validation': True,
                'enable_fuel_validation': True,
                'enable_confusion_matrix': True,
                'enable_roc_analysis': True
            },
            'realism': {
                'enable_spotting': True,
                'enable_human_influence': True,
                'enable_suppression': True,
                'enable_seasonal_effects': True,
                'max_spot_distance': 1000.0
            },
            'output': {
                'save_intermediate_results': True,
                'generate_animations': True,
                'create_detailed_reports': True,
                'output_directory': 'integrated_simulation_results'
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # 사용자 설정으로 기본값 업데이트
            self._update_config(default_config, user_config)
        
        return default_config
    
    def _update_config(self, base_config: Dict, user_config: Dict):
        """중첩된 설정 딕셔너리 업데이트"""
        for key, value in user_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._update_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def setup_models(self, fuel_map: np.ndarray, elevation_map: np.ndarray = None,
                    weather_data: Dict = None, human_activity_data: Dict = None):
        """모델 컴포넌트들 설정"""
        print("통합 시스템 모델 설정 중...")
        
        grid_size = tuple(self.config['simulation']['grid_size'])
        cell_size = self.config['simulation']['cell_size']
        
        # CA 모델 설정
        self.ca_model = AdvancedCAFireModel(grid_size)
        self.ca_model.fuel_map = fuel_map
        
        # 현실적 화재 모델 설정
        self.realistic_model = RealisticFireModel(grid_size, cell_size)
        self.realistic_model.fuel_map = fuel_map
        self.realistic_model.elevation_map = elevation_map
        
        # 기상 모델 설정
        if weather_data:
            self.weather_model = IntegratedWeatherModel()
            self.realistic_model.weather_conditions = DetailedWeatherConditions(**weather_data)
        
        # 지형 모델 설정
        if elevation_map is not None:
            self.terrain_model = TopographicFireModel()
            self.terrain_model.load_dem_data(elevation_map)
        
        # 인간 활동 데이터 설정
        if human_activity_data:
            self.realistic_model.human_activity = HumanActivity(**human_activity_data)
        
        # 연료 수분 모델 설정
        base_moisture = {
            'TL1': 0.12, 'TL2': 0.15, 'TL3': 0.18,
            'TU1': 0.10, 'TU2': 0.14, 'TU3': 0.16,
            'GS1': 0.08, 'GS2': 0.10, 'GS3': 0.12,
            'GR1': 0.06, 'GR2': 0.08,
            'SB1': 0.11, 'SB2': 0.13
        }
        self.realistic_model.set_fuel_moisture_model(base_moisture)
        
        print("모델 설정 완료")
    
    def run_integrated_simulation(self, ignition_points: List[Tuple[int, int]],
                                actual_fire_data: np.ndarray = None) -> Dict:
        """통합 시뮬레이션 실행"""
        print("통합 시뮬레이션 시작...")
        
        if self.ca_model is None:
            raise ValueError("모델이 설정되지 않았습니다. setup_models()를 먼저 실행하세요.")
        
        max_steps = self.config['simulation']['max_steps']
        validation_interval = self.config['simulation']['validation_interval']
        
        # 시뮬레이션 상태 초기화
        current_grid = np.zeros(self.ca_model.grid.shape, dtype=int)
        for i, j in ignition_points:
            if 0 <= i < current_grid.shape[0] and 0 <= j < current_grid.shape[1]:
                current_grid[i, j] = 1
        
        # 결과 저장용
        step_history = []
        validation_history = []
        realism_history = []
        
        # 시뮬레이션 루프
        for step in range(max_steps):
            print(f"단계 {step + 1}/{max_steps} 진행 중...")
            
            # 기본 CA 규칙 적용
            new_grid = self.ca_model._apply_fire_rules(current_grid)
            
            # 현실성 향상 기능 적용
            if self.config['realism']['enable_spotting']:
                spotting_ignitions = self.realistic_model.simulate_spotting(
                    new_grid, self.config['realism']['max_spot_distance']
                )
                for i, j in spotting_ignitions:
                    new_grid[i, j] = 1
            
            if self.config['realism']['enable_human_influence']:
                new_grid = self.realistic_model.apply_human_influence(new_grid)
            
            if self.config['realism']['enable_suppression']:
                # 간단한 진압 활동 시뮬레이션
                suppression_resources = self._generate_suppression_resources(new_grid)
                new_grid = self.realistic_model.simulate_suppression_activities(
                    new_grid, suppression_resources
                )
            
            # 화재 행동 분석
            behavior_data = self.realistic_model.calculate_fire_behavior(new_grid)
            
            # 계절별 효과 적용
            if self.config['realism']['enable_seasonal_effects']:
                seasonal_effects = self.realistic_model.calculate_seasonal_effects(datetime.now())
                # 계절 효과를 확산 확률에 반영
                self.ca_model.base_spread_prob *= seasonal_effects['combined_factor']
            
            current_grid = new_grid
            step_history.append(current_grid.copy())
            
            # 중간 검증 (지정된 간격마다)
            if (step + 1) % validation_interval == 0:
                interim_results = {
                    'final_grid': current_grid,
                    'step_history': step_history,
                    'fuel_map': self.ca_model.fuel_map
                }
                
                # 검증 실행
                interim_validation = self._run_interim_validation(interim_results, actual_fire_data)
                validation_history.append(interim_validation)
                
                # 현실성 지표 계산
                realism_metrics = self.realistic_model.get_realism_metrics()
                realism_history.append(realism_metrics)
                
                # 성능 모니터링
                self._monitor_performance(interim_validation, realism_metrics, step + 1)
            
            # 화재가 완전히 꺼졌으면 종료
            if np.sum(current_grid == 1) == 0:
                print(f"화재가 {step + 1}단계에서 완전히 진압되었습니다.")
                break
        
        # 최종 결과 정리
        final_results = {
            'final_grid': current_grid,
            'step_history': step_history,
            'fuel_map': self.ca_model.fuel_map,
            'validation_history': validation_history,
            'realism_history': realism_history,
            'behavior_data': behavior_data,
            'total_steps': len(step_history)
        }
        
        self.simulation_results = final_results
        return final_results
    
    def _run_interim_validation(self, interim_results: Dict, actual_data: np.ndarray = None) -> Dict:
        """중간 검증 실행"""
        validator = ModelValidator(interim_results, actual_data)
        
        validation_results = {}
        
        if self.config['validation']['enable_pattern_validation']:
            validation_results['pattern'] = validator.validate_spread_pattern(actual_data)
        
        if self.config['validation']['enable_temporal_validation']:
            validation_results['temporal'] = validator.validate_temporal_progression()
        
        if self.config['validation']['enable_fuel_validation']:
            validation_results['fuel'] = validator.validate_fuel_response()
        
        if actual_data is not None:
            if self.config['validation']['enable_confusion_matrix']:
                validation_results['confusion_matrix'] = validator.calculate_confusion_matrix(actual_data)
            
            if self.config['validation']['enable_roc_analysis']:
                validation_results['roc'] = validator.calculate_roc_metrics(actual_data)
        
        return validation_results
    
    def _generate_suppression_resources(self, current_grid: np.ndarray) -> Dict:
        """진압 자원 자동 생성"""
        fire_locations = np.where(current_grid == 1)
        
        if len(fire_locations[0]) == 0:
            return {}
        
        # 화재 중심점 계산
        fire_center_i = int(np.mean(fire_locations[0]))
        fire_center_j = int(np.mean(fire_locations[1]))
        
        # 화재 크기에 따른 자원 배치
        fire_size = len(fire_locations[0])
        
        resources = {}
        
        if fire_size > 50:  # 큰 화재
            # 지상 소방대
            resources['ground_crews'] = [
                {'location': (fire_center_i - 5, fire_center_j), 'effectiveness': 0.8, 'range': 3},
                {'location': (fire_center_i + 5, fire_center_j), 'effectiveness': 0.8, 'range': 3},
                {'location': (fire_center_i, fire_center_j - 5), 'effectiveness': 0.8, 'range': 3},
                {'location': (fire_center_i, fire_center_j + 5), 'effectiveness': 0.8, 'range': 3}
            ]
            
            # 항공 살수
            resources['aerial_drops'] = [
                {'center': (fire_center_i, fire_center_j), 'radius': 8, 'effectiveness': 0.9}
            ]
        
        elif fire_size > 20:  # 중간 화재
            resources['ground_crews'] = [
                {'location': (fire_center_i, fire_center_j), 'effectiveness': 0.8, 'range': 4}
            ]
        
        return resources
    
    def _monitor_performance(self, validation_results: Dict, realism_metrics: Dict, step: int):
        """성능 모니터링"""
        performance_data = {
            'step': step,
            'timestamp': datetime.now().isoformat(),
            'validation_score': 0.0,
            'realism_score': 0.0,
            'combined_score': 0.0
        }
        
        # 검증 점수 계산
        validation_scores = []
        if 'pattern' in validation_results:
            compactness = validation_results['pattern'].get('compactness', 0)
            validation_scores.append(compactness)
        
        if 'confusion_matrix' in validation_results:
            f1_score = validation_results['confusion_matrix'].get('f1_score', 0)
            validation_scores.append(f1_score)
        
        if validation_scores:
            performance_data['validation_score'] = np.mean(validation_scores)
        
        # 현실성 점수 계산
        realism_score = 0.0
        if realism_metrics.get('spotting_events', 0) > 0:
            realism_score += 0.3
        if realism_metrics.get('fire_behavior_diversity', 0) > 1:
            realism_score += 0.4
        if realism_metrics.get('max_fire_intensity', 0) > 0:
            realism_score += 0.3
        
        performance_data['realism_score'] = realism_score
        performance_data['combined_score'] = (performance_data['validation_score'] + realism_score) / 2
        
        self.performance_history.append(performance_data)
        
        # 개선 제안 생성
        self._generate_improvement_suggestions(performance_data, validation_results, realism_metrics)
    
    def _generate_improvement_suggestions(self, performance_data: Dict, 
                                        validation_results: Dict, realism_metrics: Dict):
        """자동 개선 제안 생성"""
        suggestions = []
        
        # 검증 점수가 낮은 경우
        if performance_data['validation_score'] < 0.5:
            suggestions.append({
                'category': 'validation',
                'priority': 'high',
                'suggestion': 'CA 규칙 파라미터 조정 필요',
                'details': '확산 확률 또는 이웃 규칙을 재검토하세요'
            })
        
        # 현실성 점수가 낮은 경우
        if performance_data['realism_score'] < 0.3:
            suggestions.append({
                'category': 'realism',
                'priority': 'medium',
                'suggestion': '현실성 기능 활성화 검토',
                'details': '비화, 인간 활동, 진압 활동 모델링을 강화하세요'
            })
        
        # 특정 문제들 체크
        if 'pattern' in validation_results:
            compactness = validation_results['pattern'].get('compactness', 0)
            if compactness < 0.3:
                suggestions.append({
                    'category': 'pattern',
                    'priority': 'medium',
                    'suggestion': '화재 확산 패턴이 너무 분산됨',
                    'details': '이웃 규칙을 더 집중적으로 설정하거나 연료 연속성을 확인하세요'
                })
        
        if realism_metrics.get('spotting_events', 0) == 0:
            suggestions.append({
                'category': 'spotting',
                'priority': 'low',
                'suggestion': '비화 현상이 관찰되지 않음',
                'details': '풍속이나 화재 강도 조건을 확인하세요'
            })
        
        # 중복 제거 후 저장
        for suggestion in suggestions:
            if suggestion not in self.improvement_suggestions:
                self.improvement_suggestions.append(suggestion)
    
    def run_comprehensive_validation(self, actual_fire_data: np.ndarray = None) -> Dict:
        """종합적인 모델 검증 실행"""
        print("종합 검증 분석 시작...")
        
        if not self.simulation_results:
            raise ValueError("시뮬레이션을 먼저 실행하세요")
        
        # 가상 실제 데이터 생성 (실제 데이터가 없는 경우)
        if actual_fire_data is None:
            print("실제 데이터가 없어 가상 데이터를 생성합니다")
            final_grid = self.simulation_results['final_grid']
            actual_fire_data = create_synthetic_actual_data(final_grid, noise_level=0.15)
        
        # 종합 검증기 생성
        self.validator = ModelValidator(self.simulation_results, actual_fire_data)
        
        # 모든 검증 수행
        validation_results = {}\n        
        # 확산 패턴 검증
        validation_results['spread_pattern'] = self.validator.validate_spread_pattern(actual_fire_data)
        
        # 시간적 진행 검증
        validation_results['temporal_progression'] = self.validator.validate_temporal_progression()
        
        # 연료별 반응 검증
        validation_results['fuel_response'] = self.validator.validate_fuel_response()
        
        # 혼동 행렬
        validation_results['confusion_matrix'] = self.validator.calculate_confusion_matrix(actual_fire_data)
        
        # ROC 분석
        validation_results['roc_metrics'] = self.validator.calculate_roc_metrics(actual_fire_data)
        
        self.validation_results = validation_results
        return validation_results
    
    def generate_comprehensive_report(self, output_dir: str = None) -> str:
        """종합 보고서 생성"""
        print("종합 보고서 생성 중...")
        
        if output_dir is None:
            output_dir = self.config['output']['output_directory']
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 보고서 데이터 준비
        report_data = {
            'metadata': {
                'generation_time': datetime.now().isoformat(),
                'simulation_config': self.config,
                'total_simulation_steps': self.simulation_results.get('total_steps', 0)
            },
            'simulation_summary': self._generate_simulation_summary(),
            'validation_results': self.validation_results,
            'realism_metrics': self.realistic_model.get_realism_metrics() if self.realistic_model else {},
            'performance_history': self.performance_history,
            'improvement_suggestions': self.improvement_suggestions
        }
        
        # JSON 보고서 저장
        report_path = os.path.join(output_dir, 'comprehensive_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # 시각화 생성
        if self.config['output']['create_detailed_reports']:
            self._create_comprehensive_visualizations(output_dir)
        
        # 애니메이션 생성
        if self.config['output']['generate_animations']:
            self._create_simulation_animation(output_dir)
        
        # 요약 보고서 생성
        self._create_summary_report(output_dir, report_data)
        
        print(f"종합 보고서가 {output_dir}에 저장되었습니다")
        return report_path
    
    def _generate_simulation_summary(self) -> Dict:
        """시뮬레이션 요약 생성"""
        if not self.simulation_results:
            return {}
        
        final_grid = self.simulation_results['final_grid']
        total_burned = np.sum(final_grid == 2)
        total_cells = final_grid.size
        
        summary = {
            'total_burned_area': int(total_burned),
            'burn_percentage': float(total_burned / total_cells * 100),
            'total_simulation_steps': self.simulation_results.get('total_steps', 0),
            'final_fire_size': int(np.sum(final_grid == 1))
        }
        
        # 연료별 연소 통계
        if 'fuel_map' in self.simulation_results:
            fuel_map = self.simulation_results['fuel_map']
            fuel_stats = {}
            
            unique_fuels = np.unique(fuel_map)
            for fuel_type in unique_fuels:
                fuel_mask = (fuel_map == fuel_type)
                fuel_burned = np.logical_and(fuel_mask, final_grid == 2)
                
                total_fuel = np.sum(fuel_mask)
                burned_fuel = np.sum(fuel_burned)
                
                fuel_stats[str(fuel_type)] = {
                    'total_cells': int(total_fuel),
                    'burned_cells': int(burned_fuel),
                    'burn_ratio': float(burned_fuel / total_fuel) if total_fuel > 0 else 0.0
                }
            
            summary['fuel_statistics'] = fuel_stats
        
        return summary
    
    def _create_comprehensive_visualizations(self, output_dir: str):
        """종합적인 시각화 생성"""
        try:
            # 1. 성능 추세 플롯
            self._plot_performance_trends(output_dir)
            
            # 2. 현실성 지표 플롯
            self._plot_realism_metrics(output_dir)
            
            # 3. 검증 결과 대시보드
            self._create_validation_dashboard(output_dir)
            
            # 4. 화재 진행 분석
            self._plot_fire_progression(output_dir)
            
        except Exception as e:
            print(f"시각화 생성 중 오류: {e}")
    
    def _plot_performance_trends(self, output_dir: str):
        """성능 추세 시각화"""
        if not self.performance_history:
            return
        
        df = pd.DataFrame(self.performance_history)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 검증 점수 추세
        axes[0, 0].plot(df['step'], df['validation_score'], 'b-', label='Validation Score')
        axes[0, 0].set_title('Validation Score Trend')
        axes[0, 0].set_xlabel('Simulation Step')
        axes[0, 0].set_ylabel('Score')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].legend()
        
        # 현실성 점수 추세
        axes[0, 1].plot(df['step'], df['realism_score'], 'r-', label='Realism Score')
        axes[0, 1].set_title('Realism Score Trend')
        axes[0, 1].set_xlabel('Simulation Step')
        axes[0, 1].set_ylabel('Score')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].legend()
        
        # 종합 점수 추세
        axes[1, 0].plot(df['step'], df['combined_score'], 'g-', label='Combined Score')
        axes[1, 0].set_title('Combined Score Trend')
        axes[1, 0].set_xlabel('Simulation Step')
        axes[1, 0].set_ylabel('Score')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].legend()
        
        # 점수 분포
        scores = [df['validation_score'], df['realism_score'], df['combined_score']]
        labels = ['Validation', 'Realism', 'Combined']
        axes[1, 1].boxplot(scores, labels=labels)
        axes[1, 1].set_title('Score Distribution')
        axes[1, 1].set_ylabel('Score')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'performance_trends.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_realism_metrics(self, output_dir: str):
        """현실성 지표 시각화"""
        if not self.realistic_model:
            return
        
        realism_data = self.realistic_model.get_realism_metrics()
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 비화 이벤트 분석
        if self.realistic_model.spotting_events:
            spotting_df = pd.DataFrame(self.realistic_model.spotting_events)
            axes[0, 0].scatter(spotting_df['distance'], spotting_df['wind_speed'], alpha=0.6)
            axes[0, 0].set_xlabel('Spotting Distance (m)')
            axes[0, 0].set_ylabel('Wind Speed (m/s)')
            axes[0, 0].set_title(f'Spotting Events (n={len(spotting_df)})')
            axes[0, 0].grid(True, alpha=0.3)
        else:
            axes[0, 0].text(0.5, 0.5, 'No Spotting Events', ha='center', va='center',
                           transform=axes[0, 0].transAxes)
            axes[0, 0].set_title('Spotting Events')
        
        # 화재 강도 분포
        if hasattr(self.realistic_model, 'fire_intensity_map'):
            intensity_data = self.realistic_model.fire_intensity_map[self.realistic_model.fire_intensity_map > 0]
            if len(intensity_data) > 0:
                axes[0, 1].hist(intensity_data, bins=20, alpha=0.7, color='orange')
                axes[0, 1].set_xlabel('Fire Intensity (kW/m)')
                axes[0, 1].set_ylabel('Frequency')
                axes[0, 1].set_title('Fire Intensity Distribution')
                axes[0, 1].grid(True, alpha=0.3)
        
        # 화염 길이 분포
        if hasattr(self.realistic_model, 'flame_length_map'):
            flame_data = self.realistic_model.flame_length_map[self.realistic_model.flame_length_map > 0]
            if len(flame_data) > 0:
                axes[1, 0].hist(flame_data, bins=20, alpha=0.7, color='red')
                axes[1, 0].set_xlabel('Flame Length (m)')
                axes[1, 0].set_ylabel('Frequency')
                axes[1, 0].set_title('Flame Length Distribution')
                axes[1, 0].grid(True, alpha=0.3)
        
        # 현실성 지표 요약
        metrics_text = f"Spotting Events: {realism_data.get('spotting_events', 0)}\n"
        metrics_text += f"Max Fire Intensity: {realism_data.get('max_fire_intensity', 0):.1f} kW/m\n"
        metrics_text += f"Mean Flame Length: {realism_data.get('mean_flame_length', 0):.1f} m\n"
        metrics_text += f"Behavior Diversity: {realism_data.get('fire_behavior_diversity', 0)}"
        
        axes[1, 1].text(0.1, 0.5, metrics_text, transform=axes[1, 1].transAxes,
                       fontsize=12, verticalalignment='center',
                       bbox=dict(boxstyle='round', facecolor='lightgreen'))
        axes[1, 1].set_title('Realism Metrics Summary')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'realism_metrics.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_validation_dashboard(self, output_dir: str):
        """검증 결과 대시보드 생성"""
        if not self.validation_results:
            return
        
        # 검증 모듈의 시각화 기능 활용
        if self.validator:
            self.validator.generate_validation_report(output_dir)
    
    def _plot_fire_progression(self, output_dir: str):
        """화재 진행 분석 시각화"""
        if not self.simulation_results or 'step_history' not in self.simulation_results:
            return
        
        step_history = self.simulation_results['step_history']
        
        # 화재 면적 진행
        burned_areas = []
        active_fires = []
        
        for grid in step_history:
            burned_areas.append(np.sum(grid == 2))
            active_fires.append(np.sum(grid == 1))
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 화재 면적 진행
        steps = range(1, len(burned_areas) + 1)
        axes[0, 0].plot(steps, burned_areas, 'b-', label='Burned Area')
        axes[0, 0].set_xlabel('Simulation Step')
        axes[0, 0].set_ylabel('Burned Cells')
        axes[0, 0].set_title('Cumulative Burned Area')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].legend()
        
        # 활성 화재 진행
        axes[0, 1].plot(steps, active_fires, 'r-', label='Active Fire')
        axes[0, 1].set_xlabel('Simulation Step')
        axes[0, 1].set_ylabel('Active Fire Cells')
        axes[0, 1].set_title('Active Fire Progression')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].legend()
        
        # 연소율 변화
        burn_rates = np.diff(burned_areas)
        if len(burn_rates) > 0:
            axes[1, 0].plot(range(2, len(burned_areas) + 1), burn_rates, 'g-')
            axes[1, 0].set_xlabel('Simulation Step')
            axes[1, 0].set_ylabel('Burn Rate (cells/step)')
            axes[1, 0].set_title('Burn Rate Over Time')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 최종 화재 맵
        if step_history:
            final_grid = step_history[-1]
            im = axes[1, 1].imshow(final_grid, cmap='RdYlBu_r')
            axes[1, 1].set_title('Final Fire State')
            plt.colorbar(im, ax=axes[1, 1])
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'fire_progression.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_simulation_animation(self, output_dir: str):
        """시뮬레이션 애니메이션 생성"""
        try:
            from matplotlib.animation import FuncAnimation
            
            if not self.simulation_results or 'step_history' not in self.simulation_results:
                return
            
            step_history = self.simulation_results['step_history']
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            def animate(frame):
                ax.clear()
                im = ax.imshow(step_history[frame], cmap='RdYlBu_r', vmin=0, vmax=2)
                ax.set_title(f'Fire Simulation - Step {frame + 1}')
                return [im]
            
            anim = FuncAnimation(fig, animate, frames=len(step_history), 
                               interval=200, blit=False, repeat=True)
            
            anim_path = os.path.join(output_dir, 'fire_simulation.gif')
            anim.save(anim_path, writer='pillow', fps=5)
            plt.close()
            
            print(f"애니메이션이 {anim_path}에 저장되었습니다")
            
        except ImportError:
            print("애니메이션 생성을 위해 추가 패키지가 필요합니다")
        except Exception as e:
            print(f"애니메이션 생성 중 오류: {e}")
    
    def _create_summary_report(self, output_dir: str, report_data: Dict):
        """요약 보고서 (마크다운) 생성"""
        summary_path = os.path.join(output_dir, 'simulation_summary.md')
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# 통합 화재 시뮬레이션 보고서\n\n")
            
            # 메타데이터
            f.write("## 시뮬레이션 개요\n")
            f.write(f"- 생성 시간: {report_data['metadata']['generation_time']}\n")
            f.write(f"- 총 단계 수: {report_data['metadata']['total_simulation_steps']}\n\n")
            
            # 시뮬레이션 요약
            if 'simulation_summary' in report_data:
                summary = report_data['simulation_summary']
                f.write("## 시뮬레이션 결과\n")
                f.write(f"- 총 연소 면적: {summary.get('total_burned_area', 0)} 셀\n")
                f.write(f"- 연소 비율: {summary.get('burn_percentage', 0):.2f}%\n")
                f.write(f"- 최종 화재 크기: {summary.get('final_fire_size', 0)} 셀\n\n")
            
            # 검증 결과 요약
            if 'validation_results' in report_data and report_data['validation_results']:
                f.write("## 검증 결과\n")
                
                if 'confusion_matrix' in report_data['validation_results']:
                    cm = report_data['validation_results']['confusion_matrix']
                    f.write(f"- 정확도: {cm.get('accuracy', 0):.3f}\n")
                    f.write(f"- 정밀도: {cm.get('precision', 0):.3f}\n")
                    f.write(f"- 재현율: {cm.get('recall', 0):.3f}\n")
                    f.write(f"- F1 점수: {cm.get('f1_score', 0):.3f}\n\n")
            
            # 현실성 지표
            if 'realism_metrics' in report_data and report_data['realism_metrics']:
                realism = report_data['realism_metrics']
                f.write("## 현실성 지표\n")
                f.write(f"- 비화 이벤트: {realism.get('spotting_events', 0)}회\n")
                f.write(f"- 최대 화재 강도: {realism.get('max_fire_intensity', 0):.1f} kW/m\n")
                f.write(f"- 평균 화염 길이: {realism.get('mean_flame_length', 0):.1f} m\n\n")
            
            # 개선 제안
            if report_data.get('improvement_suggestions'):
                f.write("## 개선 제안\n")
                for suggestion in report_data['improvement_suggestions']:
                    priority = suggestion.get('priority', 'medium')
                    f.write(f"- **{priority.upper()}**: {suggestion.get('suggestion', '')}\n")
                    f.write(f"  - {suggestion.get('details', '')}\n")
                f.write("\n")
            
            f.write("---\n")
            f.write("*이 보고서는 통합 검증 및 현실성 시스템에 의해 자동 생성되었습니다.*\n")
        
        print(f"요약 보고서가 {summary_path}에 저장되었습니다")

# 사용 예시 함수
def run_example_simulation():
    """예시 시뮬레이션 실행"""
    print("통합 검증 및 현실성 시스템 예시 실행")
    
    # 시스템 초기화
    system = IntegratedValidationSystem()
    
    # 테스트 데이터 생성
    grid_size = (80, 80)
    fuel_map = np.random.choice(['TL1', 'TL2', 'GS1', 'GS2', 'TU1'], size=grid_size)
    elevation_map = np.random.randint(100, 800, size=grid_size)
    
    # 기상 데이터
    weather_data = {
        'temperature': 32.0,
        'relative_humidity': 30.0,
        'wind_speed': 12.0,
        'wind_direction': 225.0,
        'atmospheric_pressure': 1013.0,
        'solar_radiation': 750.0,
        'precipitation': 0.0,
        'drought_index': 0.7,
        'fire_weather_index': 75.0,
        'stability_class': 'B'
    }
    
    # 인간 활동 데이터
    human_data = {
        'population_density': 0.5,
        'road_density': 0.3,
        'recreation_areas': [(20, 20), (60, 60)],
        'industrial_sites': [(30, 50)],
        'power_lines': [(10, 10, 70, 70)],
        'ignition_risk_map': np.random.random(grid_size) * 0.8
    }
    
    # 모델 설정
    system.setup_models(fuel_map, elevation_map, weather_data, human_data)
    
    # 시뮬레이션 실행
    ignition_points = [(40, 40), (42, 42)]
    results = system.run_integrated_simulation(ignition_points)
    
    # 종합 검증
    validation_results = system.run_comprehensive_validation()
    
    # 보고서 생성
    report_path = system.generate_comprehensive_report("example_simulation_results")
    
    print(f"예시 시뮬레이션 완료: {report_path}")
    return system

if __name__ == "__main__":
    run_example_simulation()
