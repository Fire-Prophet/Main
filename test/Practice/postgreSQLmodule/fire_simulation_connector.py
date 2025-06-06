#!/usr/bin/env python3
"""
🔥 화재 시뮬레이션 연결기 (Fire Simulation Connector)
==================================================

처리된 PostgreSQL 데이터를 화재 시뮬레이션 모델과 연결하는 클래스입니다.
공간 데이터를 격자 형태로 변환하고 화재 모델의 입력 형식에 맞게 준비합니다.

주요 기능:
- 벡터 데이터 → 격자 데이터 변환
- Anderson 13 연료 모델 격자 생성
- 토양 수분 및 위험도 격자 생성
- 고도/경사도 격자 생성
- 화재 모델 호환 형식 변환
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
from pathlib import Path
import json
from scipy.spatial import cKDTree
from scipy.interpolate import griddata
import warnings

class FireSimulationConnector:
    """
    처리된 공간 데이터를 화재 시뮬레이션 모델에 연결하는 클래스
    """
    
    def __init__(self, grid_size: Tuple[int, int] = (100, 100)):
        """
        화재 시뮬레이션 연결기 초기화
        
        Args:
            grid_size: 시뮬레이션 격자 크기 (rows, cols)
        """
        self.grid_size = grid_size
        self.logger = self._setup_logger()
        
        # Anderson 13 연료 모델 매핑
        self.fuel_model_properties = {
            'GR1': {'spread_rate': 0.8, 'flame_length': 0.5, 'heat_content': 15000},
            'GR2': {'spread_rate': 1.2, 'flame_length': 0.8, 'heat_content': 15000},
            'GR3': {'spread_rate': 1.8, 'flame_length': 1.2, 'heat_content': 15000},
            'GS1': {'spread_rate': 0.6, 'flame_length': 0.4, 'heat_content': 14000},
            'GS2': {'spread_rate': 1.0, 'flame_length': 0.7, 'heat_content': 14000},
            'SH1': {'spread_rate': 0.5, 'flame_length': 0.3, 'heat_content': 16000},
            'SH2': {'spread_rate': 0.8, 'flame_length': 0.6, 'heat_content': 16000},
            'SH3': {'spread_rate': 1.1, 'flame_length': 0.9, 'heat_content': 16000},
            'TU1': {'spread_rate': 0.7, 'flame_length': 0.5, 'heat_content': 17000},
            'TU2': {'spread_rate': 1.0, 'flame_length': 0.8, 'heat_content': 17000},
            'TU3': {'spread_rate': 1.4, 'flame_length': 1.1, 'heat_content': 17000},
            'TL1': {'spread_rate': 0.4, 'flame_length': 0.2, 'heat_content': 18000},
            'TL2': {'spread_rate': 0.6, 'flame_length': 0.4, 'heat_content': 18000},
            'TL3': {'spread_rate': 0.9, 'flame_length': 0.7, 'heat_content': 18000},
            'NB1': {'spread_rate': 0.1, 'flame_length': 0.1, 'heat_content': 5000},   # 비가연성
            'NB2': {'spread_rate': 0.05, 'flame_length': 0.05, 'heat_content': 3000}, # 매우 낮은 가연성
            'WA': {'spread_rate': 0.0, 'flame_length': 0.0, 'heat_content': 0},       # 물
            'UR': {'spread_rate': 0.0, 'flame_length': 0.0, 'heat_content': 0}        # 도시지역
        }
        
    def _setup_logger(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger('FireSimulationConnector')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def create_fuel_grid(self, forest_data: pd.DataFrame, soil_data: pd.DataFrame,
                        bounding_box: Tuple[float, float, float, float]) -> np.ndarray:
        """
        산림 및 토양 데이터를 기반으로 연료 모델 격자 생성
        
        Args:
            forest_data: 처리된 산림 데이터 (fuel_model 컬럼 포함)
            soil_data: 처리된 토양 데이터 (fire_risk_index 컬럼 포함)
            bounding_box: (min_lng, min_lat, max_lng, max_lat)
            
        Returns:
            np.ndarray: 연료 모델 격자 (shape: grid_size)
        """
        min_lng, min_lat, max_lng, max_lat = bounding_box
        rows, cols = self.grid_size
        
        # 격자 좌표 생성
        lng_coords = np.linspace(min_lng, max_lng, cols)
        lat_coords = np.linspace(max_lat, min_lat, rows)  # 위도는 역순
        lng_grid, lat_grid = np.meshgrid(lng_coords, lat_coords)
        
        # 기본 연료 모델로 초기화 (GR1: 낮은 가연성 풀)
        fuel_grid = np.full(self.grid_size, 'GR1', dtype='U4')
        
        self.logger.info(f"🔥 연료 격자 생성 시작: {rows}×{cols}")
        
        # 각 격자점에 대해 연료 모델 할당
        for i in range(rows):
            for j in range(cols):
                lng, lat = lng_grid[i, j], lat_grid[i, j]
                
                # 해당 위치의 산림 데이터 찾기
                forest_fuel = self._find_forest_fuel_at_point(forest_data, lng, lat)
                if forest_fuel:
                    fuel_grid[i, j] = forest_fuel
                    continue
                
                # 산림 데이터가 없으면 토양 데이터 기반으로 판단
                soil_risk = self._find_soil_risk_at_point(soil_data, lng, lat)
                if soil_risk is not None:
                    # 토양 위험도에 따른 기본 연료 모델 할당
                    if soil_risk >= 8:
                        fuel_grid[i, j] = 'GR3'  # 높은 위험도 → 빠른 확산 풀
                    elif soil_risk >= 5:
                        fuel_grid[i, j] = 'GR2'  # 중간 위험도 → 중간 확산 풀
                    else:
                        fuel_grid[i, j] = 'GR1'  # 낮은 위험도 → 낮은 확산 풀
        
        self.logger.info(f"✅ 연료 격자 생성 완료")
        return fuel_grid
    
    def create_moisture_grid(self, soil_data: pd.DataFrame, 
                           bounding_box: Tuple[float, float, float, float]) -> np.ndarray:
        """
        토양 수분 데이터를 기반으로 연료 수분 격자 생성
        
        Args:
            soil_data: 토양 데이터 (moisture_content 컬럼 포함)
            bounding_box: (min_lng, min_lat, max_lng, max_lat)
            
        Returns:
            np.ndarray: 연료 수분 격자 (0.0-1.0 범위)
        """
        min_lng, min_lat, max_lng, max_lat = bounding_box
        rows, cols = self.grid_size
        
        # 격자 좌표 생성
        lng_coords = np.linspace(min_lng, max_lng, cols)
        lat_coords = np.linspace(max_lat, min_lat, rows)
        lng_grid, lat_grid = np.meshgrid(lng_coords, lat_coords)
        
        # 토양 수분 데이터 포인트 추출
        if 'centroid_lng' in soil_data.columns and 'centroid_lat' in soil_data.columns:
            soil_points = soil_data[['centroid_lng', 'centroid_lat']].values
            moisture_values = soil_data['moisture_content'].values / 100.0  # 0-1 범위로 정규화
        else:
            # 중심점이 없으면 공간 데이터에서 추출
            soil_points = []
            moisture_values = []
            
            for _, row in soil_data.iterrows():
                try:
                    # WKT에서 중심점 추출 (간단한 파싱)
                    geom = row['geom']
                    if 'POLYGON' in geom:
                        # 간단한 중심점 계산 (실제로는 더 정교한 파싱 필요)
                        coords = self._extract_polygon_center(geom)
                        if coords:
                            soil_points.append(coords)
                            moisture_values.append(row['moisture_content'] / 100.0)
                except Exception as e:
                    continue
            
            soil_points = np.array(soil_points)
            moisture_values = np.array(moisture_values)
        
        if len(soil_points) == 0:
            self.logger.warning("⚠️ 토양 수분 데이터 없음, 기본값 0.3 사용")
            return np.full(self.grid_size, 0.3)
        
        # 격자점에 수분값 보간
        grid_points = np.column_stack((lng_grid.ravel(), lat_grid.ravel()))
        
        try:
            # 최근접 이웃 보간 사용
            tree = cKDTree(soil_points)
            _, indices = tree.query(grid_points, k=1)
            moisture_grid = moisture_values[indices].reshape(self.grid_size)
            
            self.logger.info(f"💧 수분 격자 생성 완료 (범위: {moisture_grid.min():.2f}-{moisture_grid.max():.2f})")
            return moisture_grid
            
        except Exception as e:
            self.logger.error(f"❌ 수분 격자 생성 실패: {e}")
            return np.full(self.grid_size, 0.3)
    
    def create_elevation_grid(self, elevation_data: pd.DataFrame,
                             bounding_box: Tuple[float, float, float, float]) -> Dict[str, np.ndarray]:
        """
        고도 데이터를 기반으로 고도/경사도 격자 생성
        
        Args:
            elevation_data: 고도 데이터
            bounding_box: (min_lng, min_lat, max_lng, max_lat)
            
        Returns:
            Dict: {'elevation': 고도격자, 'slope': 경사도격자, 'aspect': 방향각격자}
        """
        min_lng, min_lat, max_lng, max_lat = bounding_box
        rows, cols = self.grid_size
        
        # 격자 좌표 생성
        lng_coords = np.linspace(min_lng, max_lng, cols)
        lat_coords = np.linspace(max_lat, min_lat, rows)
        lng_grid, lat_grid = np.meshgrid(lng_coords, lat_coords)
        
        if elevation_data.empty:
            self.logger.warning("⚠️ 고도 데이터 없음, 평지로 가정")
            return {
                'elevation': np.zeros(self.grid_size),
                'slope': np.zeros(self.grid_size),
                'aspect': np.zeros(self.grid_size)
            }
        
        # 고도 데이터 포인트
        points = elevation_data[['longitude', 'latitude']].values
        elevation_values = elevation_data['elevation'].values
        slope_values = elevation_data['slope'].values if 'slope' in elevation_data.columns else np.zeros(len(elevation_values))
        aspect_values = elevation_data['aspect'].values if 'aspect' in elevation_data.columns else np.zeros(len(elevation_values))
        
        # 격자점에 보간
        grid_points = np.column_stack((lng_grid.ravel(), lat_grid.ravel()))
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # 선형 보간
                elevation_grid = griddata(points, elevation_values, grid_points, method='linear', fill_value=0)
                slope_grid = griddata(points, slope_values, grid_points, method='linear', fill_value=0)
                aspect_grid = griddata(points, aspect_values, grid_points, method='linear', fill_value=0)
                
                # 형태 변환
                elevation_grid = elevation_grid.reshape(self.grid_size)
                slope_grid = slope_grid.reshape(self.grid_size)
                aspect_grid = aspect_grid.reshape(self.grid_size)
                
                # NaN 값 처리
                elevation_grid = np.nan_to_num(elevation_grid, nan=0.0)
                slope_grid = np.nan_to_num(slope_grid, nan=0.0) 
                aspect_grid = np.nan_to_num(aspect_grid, nan=0.0)
            
            self.logger.info(f"🏔️ 지형 격자 생성 완료 (고도 범위: {elevation_grid.min():.1f}-{elevation_grid.max():.1f}m)")
            
            return {
                'elevation': elevation_grid,
                'slope': slope_grid,
                'aspect': aspect_grid
            }
            
        except Exception as e:
            self.logger.error(f"❌ 지형 격자 생성 실패: {e}")
            return {
                'elevation': np.zeros(self.grid_size),
                'slope': np.zeros(self.grid_size),
                'aspect': np.zeros(self.grid_size)
            }
    
    def create_simulation_input(self, forest_data: pd.DataFrame, soil_data: pd.DataFrame,
                               elevation_data: pd.DataFrame, weather_data: Optional[Dict] = None,
                               bounding_box: Tuple[float, float, float, float] = None) -> Dict[str, Any]:
        """
        화재 시뮬레이션 모델의 입력 데이터 생성
        
        Args:
            forest_data: 처리된 산림 데이터
            soil_data: 처리된 토양 데이터
            elevation_data: 고도 데이터
            weather_data: 기상 데이터 (선택사항)
            bounding_box: 경계 박스
            
        Returns:
            Dict: 화재 시뮬레이션 입력 데이터
        """
        if bounding_box is None:
            # 데이터에서 경계 박스 추정
            bounding_box = self._estimate_bounding_box(forest_data, soil_data, elevation_data)
        
        self.logger.info("🔥 화재 시뮬레이션 입력 데이터 생성 시작")
        
        # 연료 모델 격자 생성
        fuel_grid = self.create_fuel_grid(forest_data, soil_data, bounding_box)
        
        # 수분 격자 생성
        moisture_grid = self.create_moisture_grid(soil_data, bounding_box)
        
        # 지형 격자 생성
        terrain_grids = self.create_elevation_grid(elevation_data, bounding_box)
        
        # 화재 시뮬레이션 입력 구조 생성
        simulation_input = {
            'grid_size': self.grid_size,
            'bounding_box': bounding_box,
            'fuel_model': fuel_grid,
            'fuel_moisture': moisture_grid,
            'elevation': terrain_grids['elevation'],
            'slope': terrain_grids['slope'],
            'aspect': terrain_grids['aspect'],
            'fuel_properties': self.fuel_model_properties,
            'weather': weather_data or self._default_weather(),
            'metadata': {
                'forest_records': len(forest_data),
                'soil_records': len(soil_data),
                'elevation_records': len(elevation_data),
                'creation_time': pd.Timestamp.now().isoformat()
            }
        }
        
        self.logger.info("✅ 화재 시뮬레이션 입력 데이터 생성 완료")
        return simulation_input
    
    def save_simulation_input(self, simulation_input: Dict[str, Any], 
                             output_path: str = "fire_simulation_input.npz") -> bool:
        """
        화재 시뮬레이션 입력 데이터를 파일로 저장
        
        Args:
            simulation_input: 시뮬레이션 입력 데이터
            output_path: 출력 파일 경로
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # NumPy 배열들과 메타데이터 분리
            arrays_to_save = {}
            metadata = {}
            
            for key, value in simulation_input.items():
                if isinstance(value, np.ndarray):
                    arrays_to_save[key] = value
                else:
                    metadata[key] = value
            
            # NumPy 파일로 저장
            np.savez_compressed(output_path, **arrays_to_save)
            
            # 메타데이터는 JSON으로 저장
            metadata_path = output_path.replace('.npz', '_metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"💾 시뮬레이션 입력 데이터 저장 완료: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 데이터 저장 실패: {e}")
            return False
    
    def _find_forest_fuel_at_point(self, forest_data: pd.DataFrame, lng: float, lat: float) -> Optional[str]:
        """점 위치에서 산림 연료 모델 찾기"""
        if 'fuel_model' not in forest_data.columns:
            return None
        
        # 간단한 거리 기반 검색 (실제로는 공간 인덱스 사용 권장)
        if 'centroid_lng' in forest_data.columns:
            distances = np.sqrt((forest_data['centroid_lng'] - lng)**2 + 
                              (forest_data['centroid_lat'] - lat)**2)
            min_idx = distances.idxmin()
            if distances[min_idx] < 0.01:  # 약 1km 이내
                return forest_data.loc[min_idx, 'fuel_model']
        
        return None
    
    def _find_soil_risk_at_point(self, soil_data: pd.DataFrame, lng: float, lat: float) -> Optional[float]:
        """점 위치에서 토양 위험도 찾기"""
        if 'fire_risk_index' not in soil_data.columns:
            return None
        
        if 'centroid_lng' in soil_data.columns:
            distances = np.sqrt((soil_data['centroid_lng'] - lng)**2 + 
                              (soil_data['centroid_lat'] - lat)**2)
            min_idx = distances.idxmin()
            if distances[min_idx] < 0.01:  # 약 1km 이내
                return soil_data.loc[min_idx, 'fire_risk_index']
        
        return None
    
    def _extract_polygon_center(self, wkt_geom: str) -> Optional[Tuple[float, float]]:
        """WKT POLYGON에서 중심점 추출 (간단한 구현)"""
        try:
            if 'POLYGON' in wkt_geom:
                # 간단한 정규식 파싱 (실제로는 shapely 등 사용 권장)
                coords_str = wkt_geom.split('((')[1].split('))')[0]
                coords = []
                for coord_pair in coords_str.split(','):
                    lng, lat = map(float, coord_pair.strip().split())
                    coords.append((lng, lat))
                
                # 중심점 계산
                lngs = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                return (sum(lngs) / len(lngs), sum(lats) / len(lats))
        except:
            pass
        
        return None
    
    def _estimate_bounding_box(self, forest_data: pd.DataFrame, soil_data: pd.DataFrame,
                              elevation_data: pd.DataFrame) -> Tuple[float, float, float, float]:
        """데이터에서 경계 박스 추정"""
        all_lngs, all_lats = [], []
        
        # 고도 데이터에서 좌표 추출
        if not elevation_data.empty and 'longitude' in elevation_data.columns:
            all_lngs.extend(elevation_data['longitude'].tolist())
            all_lats.extend(elevation_data['latitude'].tolist())
        
        # 중심점 데이터가 있으면 추가
        for df in [forest_data, soil_data]:
            if 'centroid_lng' in df.columns:
                all_lngs.extend(df['centroid_lng'].tolist())
                all_lats.extend(df['centroid_lat'].tolist())
        
        if not all_lngs:
            # 기본값 (한반도 중부)
            return (127.0, 37.0, 127.5, 37.5)
        
        return (min(all_lngs), min(all_lats), max(all_lngs), max(all_lats))
    
    def _default_weather(self) -> Dict[str, float]:
        """기본 기상 조건"""
        return {
            'wind_speed': 5.0,      # m/s
            'wind_direction': 0.0,   # 도 (북쪽 = 0)
            'temperature': 25.0,     # 섭씨
            'humidity': 50.0,        # %
            'pressure': 1013.25      # hPa
        }


if __name__ == "__main__":
    # 사용 예제
    print("🔥 화재 시뮬레이션 연결기 테스트")
    
    # 샘플 데이터 생성
    forest_data = pd.DataFrame({
        'fuel_model': ['TL2', 'TL3', 'GR2'],
        'centroid_lng': [127.1, 127.2, 127.3],
        'centroid_lat': [37.1, 37.2, 37.3]
    })
    
    soil_data = pd.DataFrame({
        'moisture_content': [30, 40, 20],
        'fire_risk_index': [6, 4, 8],
        'centroid_lng': [127.15, 127.25, 127.35],
        'centroid_lat': [37.15, 37.25, 37.35]
    })
    
    elevation_data = pd.DataFrame({
        'longitude': [127.1, 127.2, 127.3],
        'latitude': [37.1, 37.2, 37.3],
        'elevation': [100, 150, 200],
        'slope': [5, 10, 15]
    })
    
    # 연결기 생성 및 테스트
    connector = FireSimulationConnector(grid_size=(50, 50))
    
    bounding_box = (127.0, 37.0, 127.4, 37.4)
    simulation_input = connector.create_simulation_input(
        forest_data, soil_data, elevation_data, bounding_box=bounding_box
    )
    
    print(f"✅ 시뮬레이션 입력 데이터 생성 완료")
    print(f"   - 격자 크기: {simulation_input['grid_size']}")
    print(f"   - 연료 모델 종류: {np.unique(simulation_input['fuel_model'])}")
    print(f"   - 수분 범위: {simulation_input['fuel_moisture'].min():.2f}-{simulation_input['fuel_moisture'].max():.2f}")
    print(f"   - 고도 범위: {simulation_input['elevation'].min():.1f}-{simulation_input['elevation'].max():.1f}m")
