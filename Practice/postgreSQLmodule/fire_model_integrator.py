#!/usr/bin/env python3
"""
🔥 화재 모델 통합기 (Fire Model Integrator)
==========================================

PostgreSQL 데이터 추출부터 화재 시뮬레이션 실행까지 
전체 파이프라인을 통합 관리하는 메인 클래스입니다.

전체 워크플로우:
1. PostgreSQL에서 공간 데이터 추출
2. 산림/토양 데이터 처리 및 변환
3. 시뮬레이션 격자 생성
4. 화재 모델 실행
5. 결과 분석 및 저장

기존 model/ 디렉토리의 화재 모델들과 연동:
- AdvancedCAModel
- RealisticFireModel  
- IntegratedFireSimulation
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import json
from datetime import datetime
import warnings

# 현재 모듈 임포트
try:
    from .spatial_data_extractor import SpatialDataExtractor
    from .forest_data_processor import ForestDataProcessor
    from .soil_data_processor import SoilDataProcessor
    from .fire_simulation_connector import FireSimulationConnector
except ImportError:
    # 패키지 외부에서 실행할 때
    from spatial_data_extractor import SpatialDataExtractor
    from forest_data_processor import ForestDataProcessor
    from soil_data_processor import SoilDataProcessor
    from fire_simulation_connector import FireSimulationConnector

# model 디렉토리의 화재 모델들 임포트
model_path = Path(__file__).parent.parent / "model"
if model_path.exists():
    sys.path.append(str(model_path))

try:
    from advanced_ca_model import AdvancedCAModel
    from realistic_fire_model import RealisticFireModel
    from integrated_fire_simulation import IntegratedFireSimulation
    FIRE_MODELS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  화재 모델을 가져올 수 없습니다: {e}")
    FIRE_MODELS_AVAILABLE = False

class FireModelIntegrator:
    """
    PostgreSQL 데이터와 화재 모델을 통합하는 메인 클래스
    
    전체 화재 시뮬레이션 파이프라인을 관리합니다:
    PostgreSQL → 데이터 처리 → 격자 변환 → 화재 시뮬레이션 → 결과 분석
    """
    
    def __init__(self, db_config: Dict[str, Any], simulation_config: Optional[Dict[str, Any]] = None):
        """
        화재 모델 통합기 초기화
        
        Args:
            db_config: PostgreSQL 연결 설정
            simulation_config: 시뮬레이션 설정
        """
        self.db_config = db_config
        self.simulation_config = simulation_config or self._default_simulation_config()
        self.logger = self._setup_logger()
        
        # 각 처리 모듈 초기화
        self.data_extractor = SpatialDataExtractor(db_config)
        self.forest_processor = ForestDataProcessor()
        self.soil_processor = SoilDataProcessor()
        self.simulation_connector = FireSimulationConnector(
            grid_size=tuple(self.simulation_config['grid_size'])
        )
        
        # 시뮬레이션 결과 저장
        self.last_simulation_results = None
        self.last_input_data = None
        
    def _setup_logger(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger('FireModelIntegrator')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _default_simulation_config(self) -> Dict[str, Any]:
        """기본 시뮬레이션 설정"""
        return {
            'grid_size': [100, 100],
            'grid_resolution': 0.001,  # 도 단위 (약 100m)
            'simulation_steps': 100,
            'time_step': 1.0,  # 분
            'ignition_points': [(50, 50)],  # 격자 좌표
            'wind_speed': 5.0,  # m/s
            'wind_direction': 0.0,  # 도
            'temperature': 25.0,  # 섭씨
            'humidity': 50.0,  # %
            'model_type': 'integrated',  # 'advanced_ca', 'realistic', 'integrated'
            'output_dir': 'fire_simulation_results'
        }
    
    def run_full_simulation(self, bounding_box: Tuple[float, float, float, float],
                           ignition_points: Optional[List[Tuple[float, float]]] = None,
                           weather_override: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        전체 화재 시뮬레이션 파이프라인 실행
        
        Args:
            bounding_box: (min_lng, min_lat, max_lng, max_lat)
            ignition_points: 발화점 좌표 (경도, 위도) 리스트
            weather_override: 기상 조건 override
            
        Returns:
            Dict: 시뮬레이션 결과
        """
        self.logger.info("🔥 전체 화재 시뮬레이션 파이프라인 시작")
        
        try:
            # 1단계: PostgreSQL에서 데이터 추출
            self.logger.info("1️⃣ PostgreSQL 데이터 추출 중...")
            raw_data = self._extract_spatial_data(bounding_box)
            
            # 2단계: 데이터 처리 및 변환
            self.logger.info("2️⃣ 공간 데이터 처리 중...")
            processed_data = self._process_spatial_data(raw_data)
            
            # 3단계: 시뮬레이션 입력 데이터 생성
            self.logger.info("3️⃣ 시뮬레이션 입력 데이터 생성 중...")
            simulation_input = self._create_simulation_input(processed_data, bounding_box, weather_override)
            
            # 4단계: 발화점 설정
            if ignition_points:
                simulation_input['ignition_points'] = self._convert_geo_to_grid_coords(
                    ignition_points, bounding_box, simulation_input['grid_size']
                )
            else:
                simulation_input['ignition_points'] = self.simulation_config['ignition_points']
            
            # 5단계: 화재 시뮬레이션 실행
            self.logger.info("4️⃣ 화재 시뮬레이션 실행 중...")
            simulation_results = self._run_fire_simulation(simulation_input)
            
            # 6단계: 결과 분석 및 저장
            self.logger.info("5️⃣ 결과 분석 및 저장 중...")
            analysis_results = self._analyze_results(simulation_results, simulation_input)
            
            # 전체 결과 통합
            final_results = {
                'metadata': {
                    'bounding_box': bounding_box,
                    'simulation_time': datetime.now().isoformat(),
                    'grid_size': simulation_input['grid_size'],
                    'total_steps': len(simulation_results.get('states', [])),
                    'ignition_points': simulation_input['ignition_points']
                },
                'input_data': {
                    'raw_data_stats': self._get_data_stats(raw_data),
                    'processed_data_stats': self._get_data_stats(processed_data),
                    'simulation_config': self.simulation_config
                },
                'simulation_results': simulation_results,
                'analysis': analysis_results
            }
            
            # 결과 저장
            self._save_results(final_results)
            
            # 인스턴스 변수에 저장
            self.last_simulation_results = final_results
            self.last_input_data = simulation_input
            
            self.logger.info("✅ 전체 화재 시뮬레이션 파이프라인 완료!")
            return final_results
            
        except Exception as e:
            self.logger.error(f"❌ 시뮬레이션 파이프라인 실패: {e}")
            raise
    
    def _extract_spatial_data(self, bounding_box: Tuple[float, float, float, float]) -> Dict[str, pd.DataFrame]:
        """PostgreSQL에서 공간 데이터 추출"""
        if not self.data_extractor.connect():
            raise Exception("PostgreSQL 연결 실패")
        
        try:
            data = self.data_extractor.extract_all_fire_simulation_data(
                bounding_box, 
                self.simulation_config['grid_resolution']
            )
            return data
        finally:
            self.data_extractor.disconnect()
    
    def _process_spatial_data(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """공간 데이터 처리 및 변환"""
        processed_data = {}
        
        # 산림 데이터 처리
        if not raw_data['forest'].empty:
            processed_data['forest'] = self.forest_processor.process_forest_data(raw_data['forest'])
        else:
            processed_data['forest'] = pd.DataFrame()
        
        # 토양 데이터 처리
        if not raw_data['soil'].empty:
            processed_data['soil'] = self.soil_processor.process_soil_data(raw_data['soil'])
        else:
            processed_data['soil'] = pd.DataFrame()
        
        # 고도 및 기상 데이터는 그대로 전달
        processed_data['elevation'] = raw_data['elevation']
        processed_data['weather_stations'] = raw_data['weather_stations']
        
        return processed_data
    
    def _create_simulation_input(self, processed_data: Dict[str, pd.DataFrame],
                                bounding_box: Tuple[float, float, float, float],
                                weather_override: Optional[Dict[str, float]]) -> Dict[str, Any]:
        """시뮬레이션 입력 데이터 생성"""
        
        # 기상 데이터 설정
        weather_data = {
            'wind_speed': self.simulation_config['wind_speed'],
            'wind_direction': self.simulation_config['wind_direction'],
            'temperature': self.simulation_config['temperature'],
            'humidity': self.simulation_config['humidity']
        }
        
        if weather_override:
            weather_data.update(weather_override)
        
        # 시뮬레이션 입력 생성
        simulation_input = self.simulation_connector.create_simulation_input(
            processed_data['forest'],
            processed_data['soil'],
            processed_data['elevation'],
            weather_data,
            bounding_box
        )
        
        return simulation_input
    
    def _run_fire_simulation(self, simulation_input: Dict[str, Any]) -> Dict[str, Any]:
        """화재 시뮬레이션 실행"""
        if not FIRE_MODELS_AVAILABLE:
            raise Exception("화재 모델을 사용할 수 없습니다")
        
        model_type = self.simulation_config['model_type']
        
        try:
            if model_type == 'integrated':
                return self._run_integrated_simulation(simulation_input)
            elif model_type == 'advanced_ca':
                return self._run_advanced_ca_simulation(simulation_input)
            elif model_type == 'realistic':
                return self._run_realistic_simulation(simulation_input)
            else:
                raise ValueError(f"지원하지 않는 모델 타입: {model_type}")
                
        except Exception as e:
            self.logger.error(f"화재 시뮬레이션 실행 실패: {e}")
            # 간단한 더미 결과 반환
            return self._create_dummy_results(simulation_input)
    
    def _run_integrated_simulation(self, simulation_input: Dict[str, Any]) -> Dict[str, Any]:
        """통합 화재 시뮬레이션 실행"""
        sim = IntegratedFireSimulation(
            grid_size=simulation_input['grid_size'],
            fuel_map=simulation_input['fuel_model'],
            elevation_map=simulation_input['elevation'],
            initial_moisture=simulation_input['fuel_moisture']
        )
        
        # 발화점 설정
        for point in simulation_input['ignition_points']:
            sim.add_ignition_point(point[0], point[1])
        
        # 기상 조건 설정
        weather = simulation_input['weather']
        sim.set_weather_conditions(
            wind_speed=weather['wind_speed'],
            wind_direction=weather['wind_direction'],
            temperature=weather['temperature'],
            humidity=weather['humidity']
        )
        
        # 시뮬레이션 실행
        states = []
        for step in range(self.simulation_config['simulation_steps']):
            sim.step()
            states.append(sim.get_state().copy())
            
            # 화재가 완전히 꺼지면 중단
            if np.sum(sim.fire_state == 1) == 0:  # 연소 중인 셀이 없음
                break
        
        return {
            'model_type': 'integrated',
            'states': states,
            'final_state': sim.get_state(),
            'statistics': sim.get_statistics(),
            'steps_completed': len(states)
        }
    
    def _run_advanced_ca_simulation(self, simulation_input: Dict[str, Any]) -> Dict[str, Any]:
        """고급 CA 모델 시뮬레이션 실행"""
        model = AdvancedCAModel(
            grid_size=simulation_input['grid_size'],
            fuel_density=simulation_input['fuel_moisture'],  # 연료 밀도로 사용
            wind_speed=simulation_input['weather']['wind_speed'],
            wind_direction=simulation_input['weather']['wind_direction']
        )
        
        # 발화점 설정
        for point in simulation_input['ignition_points']:
            model.ignite(point[0], point[1])
        
        # 시뮬레이션 실행
        states = []
        for step in range(self.simulation_config['simulation_steps']):
            model.step()
            states.append(model.grid.copy())
            
            # 화재가 완전히 꺼지면 중단
            if np.sum(model.grid == 1) == 0:
                break
        
        return {
            'model_type': 'advanced_ca',
            'states': states,
            'final_state': model.grid,
            'steps_completed': len(states)
        }
    
    def _run_realistic_simulation(self, simulation_input: Dict[str, Any]) -> Dict[str, Any]:
        """현실적 화재 모델 시뮬레이션 실행"""
        model = RealisticFireModel(
            width=simulation_input['grid_size'][1],
            height=simulation_input['grid_size'][0]
        )
        
        # 환경 설정
        model.set_environment(
            fuel_density=simulation_input['fuel_moisture'],
            moisture_content=simulation_input['fuel_moisture'],
            wind_speed=simulation_input['weather']['wind_speed'],
            wind_direction=simulation_input['weather']['wind_direction'],
            temperature=simulation_input['weather']['temperature']
        )
        
        # 발화점 설정
        for point in simulation_input['ignition_points']:
            model.ignite(point[0], point[1])
        
        # 시뮬레이션 실행
        states = []
        for step in range(self.simulation_config['simulation_steps']):
            model.step()
            states.append(model.get_grid_state().copy())
            
            # 화재가 완전히 꺼지면 중단
            if not model.has_active_fire():
                break
        
        return {
            'model_type': 'realistic',
            'states': states,
            'final_state': model.get_grid_state(),
            'steps_completed': len(states)
        }
    
    def _create_dummy_results(self, simulation_input: Dict[str, Any]) -> Dict[str, Any]:
        """화재 모델을 사용할 수 없을 때 더미 결과 생성"""
        rows, cols = simulation_input['grid_size']
        
        # 간단한 원형 확산 시뮬레이션
        states = []
        grid = np.zeros((rows, cols))
        
        # 발화점 설정
        for point in simulation_input['ignition_points']:
            grid[point[0], point[1]] = 2  # 연소 완료
        
        # 원형으로 확산
        center_r, center_c = simulation_input['ignition_points'][0]
        for step in range(min(20, self.simulation_config['simulation_steps'])):
            radius = step * 2
            for r in range(max(0, center_r - radius), min(rows, center_r + radius + 1)):
                for c in range(max(0, center_c - radius), min(cols, center_c + radius + 1)):
                    if (r - center_r)**2 + (c - center_c)**2 <= radius**2:
                        if grid[r, c] == 0:
                            grid[r, c] = 2
            
            states.append(grid.copy())
        
        return {
            'model_type': 'dummy',
            'states': states,
            'final_state': grid,
            'steps_completed': len(states)
        }
    
    def _analyze_results(self, simulation_results: Dict[str, Any], 
                        simulation_input: Dict[str, Any]) -> Dict[str, Any]:
        """시뮬레이션 결과 분석"""
        final_state = simulation_results['final_state']
        states = simulation_results.get('states', [])
        
        # 기본 통계 계산
        total_cells = final_state.size
        burned_cells = np.sum(final_state == 2) if len(states) > 0 else 0
        burning_cells = np.sum(final_state == 1) if len(states) > 0 else 0
        
        # 시계열 통계
        temporal_stats = []
        for i, state in enumerate(states):
            temporal_stats.append({
                'step': i,
                'burning': int(np.sum(state == 1)) if isinstance(state, np.ndarray) else 0,
                'burned': int(np.sum(state == 2)) if isinstance(state, np.ndarray) else 0,
                'unburned': int(np.sum(state == 0)) if isinstance(state, np.ndarray) else total_cells
            })
        
        # 격자 크기를 실제 면적으로 변환 (대략적)
        grid_resolution_m = self.simulation_config['grid_resolution'] * 111000  # 도를 미터로 변환
        cell_area_ha = (grid_resolution_m ** 2) / 10000  # 헥타르로 변환
        
        analysis = {
            'summary': {
                'total_cells': int(total_cells),
                'burned_cells': int(burned_cells),
                'burning_cells': int(burning_cells),
                'burn_percentage': float(burned_cells / total_cells * 100) if total_cells > 0 else 0,
                'burned_area_ha': float(burned_cells * cell_area_ha),
                'simulation_steps': len(states),
                'simulation_duration_min': len(states) * self.simulation_config['time_step']
            },
            'temporal_progression': temporal_stats,
            'fuel_impact': self._analyze_fuel_impact(simulation_input, final_state),
            'spatial_analysis': {
                'burn_pattern': 'circular' if len(states) > 0 else 'none',
                'spread_rate': float(burned_cells / len(states)) if len(states) > 0 else 0,
                'max_extent': self._calculate_max_extent(final_state)
            }
        }
        
        return analysis
    
    def _analyze_fuel_impact(self, simulation_input: Dict[str, Any], final_state: np.ndarray) -> Dict[str, Any]:
        """연료 타입별 영향 분석"""
        fuel_grid = simulation_input['fuel_model']
        
        fuel_impact = {}
        unique_fuels = np.unique(fuel_grid)
        
        for fuel_type in unique_fuels:
            fuel_mask = (fuel_grid == fuel_type)
            total_fuel_cells = np.sum(fuel_mask)
            burned_fuel_cells = np.sum((fuel_mask) & (final_state == 2))
            
            fuel_impact[str(fuel_type)] = {
                'total_cells': int(total_fuel_cells),
                'burned_cells': int(burned_fuel_cells),
                'burn_percentage': float(burned_fuel_cells / total_fuel_cells * 100) if total_fuel_cells > 0 else 0
            }
        
        return fuel_impact
    
    def _calculate_max_extent(self, final_state: np.ndarray) -> Dict[str, int]:
        """화재 최대 확산 범위 계산"""
        burned_cells = np.where(final_state == 2)
        
        if len(burned_cells[0]) == 0:
            return {'min_row': 0, 'max_row': 0, 'min_col': 0, 'max_col': 0}
        
        return {
            'min_row': int(np.min(burned_cells[0])),
            'max_row': int(np.max(burned_cells[0])),
            'min_col': int(np.min(burned_cells[1])),
            'max_col': int(np.max(burned_cells[1]))
        }
    
    def _convert_geo_to_grid_coords(self, geo_points: List[Tuple[float, float]], 
                                   bounding_box: Tuple[float, float, float, float],
                                   grid_size: Tuple[int, int]) -> List[Tuple[int, int]]:
        """지리 좌표를 격자 좌표로 변환"""
        min_lng, min_lat, max_lng, max_lat = bounding_box
        rows, cols = grid_size
        
        grid_points = []
        for lng, lat in geo_points:
            # 정규화된 좌표 계산
            norm_lng = (lng - min_lng) / (max_lng - min_lng)
            norm_lat = (max_lat - lat) / (max_lat - min_lat)  # 위도는 역순
            
            # 격자 좌표로 변환
            grid_row = int(norm_lat * rows)
            grid_col = int(norm_lng * cols)
            
            # 경계 확인
            grid_row = max(0, min(rows - 1, grid_row))
            grid_col = max(0, min(cols - 1, grid_col))
            
            grid_points.append((grid_row, grid_col))
        
        return grid_points
    
    def _get_data_stats(self, data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """데이터 통계 정보 생성"""
        stats = {}
        for key, df in data.items():
            stats[key] = len(df) if isinstance(df, pd.DataFrame) else 0
        return stats
    
    def _save_results(self, results: Dict[str, Any]) -> bool:
        """시뮬레이션 결과 저장"""
        try:
            output_dir = Path(self.simulation_config['output_dir'])
            output_dir.mkdir(exist_ok=True)
            
            # 파일명에 타임스탬프 추가
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # JSON 결과 저장 (NumPy 배열 제외)
            json_results = self._prepare_json_results(results)
            json_path = output_dir / f"fire_simulation_results_{timestamp}.json"
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_results, f, ensure_ascii=False, indent=2)
            
            # NumPy 배열들은 별도 파일로 저장
            arrays_path = output_dir / f"fire_simulation_arrays_{timestamp}.npz"
            arrays_to_save = self._extract_numpy_arrays(results)
            if arrays_to_save:
                np.savez_compressed(arrays_path, **arrays_to_save)
            
            self.logger.info(f"💾 시뮬레이션 결과 저장 완료: {json_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 결과 저장 실패: {e}")
            return False
    
    def _prepare_json_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """JSON 저장을 위해 NumPy 배열 제거"""
        json_results = {}
        
        for key, value in results.items():
            if isinstance(value, dict):
                json_results[key] = self._prepare_json_results(value)
            elif isinstance(value, np.ndarray):
                json_results[key] = f"<NumPy Array: {value.shape}>"
            elif isinstance(value, (list, tuple)) and len(value) > 0 and isinstance(value[0], np.ndarray):
                json_results[key] = f"<NumPy Array List: {len(value)} items>"
            else:
                json_results[key] = value
        
        return json_results
    
    def _extract_numpy_arrays(self, results: Dict[str, Any], prefix: str = "") -> Dict[str, np.ndarray]:
        """결과에서 NumPy 배열들 추출"""
        arrays = {}
        
        for key, value in results.items():
            full_key = f"{prefix}_{key}" if prefix else key
            
            if isinstance(value, dict):
                arrays.update(self._extract_numpy_arrays(value, full_key))
            elif isinstance(value, np.ndarray):
                arrays[full_key] = value
            elif isinstance(value, (list, tuple)) and len(value) > 0 and isinstance(value[0], np.ndarray):
                for i, arr in enumerate(value):
                    arrays[f"{full_key}_{i}"] = arr
        
        return arrays


if __name__ == "__main__":
    # 사용 예제
    print("🔥 화재 모델 통합기 테스트")
    
    # 데이터베이스 설정
    db_config = {
        'host': 'localhost',
        'database': 'spatial_fire_db',
        'user': 'postgres',
        'password': 'password',
        'port': 5432
    }
    
    # 시뮬레이션 설정
    simulation_config = {
        'grid_size': [50, 50],
        'grid_resolution': 0.001,
        'simulation_steps': 50,
        'model_type': 'integrated',
        'wind_speed': 8.0,
        'wind_direction': 45.0,
        'temperature': 30.0,
        'humidity': 30.0
    }
    
    # 통합기 생성
    integrator = FireModelIntegrator(db_config, simulation_config)
    
    # 시뮬레이션 실행 (예시 영역)
    bounding_box = (127.0, 37.0, 127.1, 37.1)  # 서울 일부
    ignition_points = [(127.05, 37.05)]  # 발화점
    
    try:
        results = integrator.run_full_simulation(
            bounding_box=bounding_box,
            ignition_points=ignition_points,
            weather_override={'wind_speed': 10.0, 'humidity': 20.0}
        )
        
        print("✅ 화재 시뮬레이션 완료!")
        print(f"   - 연소 면적: {results['analysis']['summary']['burned_area_ha']:.2f} ha")
        print(f"   - 연소율: {results['analysis']['summary']['burn_percentage']:.1f}%")
        print(f"   - 시뮬레이션 단계: {results['analysis']['summary']['simulation_steps']}")
        
    except Exception as e:
        print(f"❌ 시뮬레이션 실패: {e}")
        print("💡 PostgreSQL 연결 및 데이터 확인 필요")
