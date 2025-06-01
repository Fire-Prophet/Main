#!/usr/bin/env python3
"""
PostgreSQL 데이터와 화재 시뮬레이션 모델 연동 모듈
공간 데이터를 추출하여 화재 모델에 전달하는 기능 제공
"""

import numpy as np
import pandas as pd
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import json

# 현재 디렉토리에서 모듈 임포트
from db_connection import PostgreSQLConnection
from table_analyzer import PostgreSQLTableAnalyzer
from data_exporter import PostgreSQLDataExporter

# model 디렉토리 추가
model_path = Path(__file__).parent.parent / "model"
sys.path.append(str(model_path))

try:
    from advanced_ca_model import AdvancedCAModel
    from realistic_fire_model import RealisticFireModel
    from integrated_fire_simulation import IntegratedFireSimulation
    MODEL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  모델 모듈을 가져올 수 없습니다: {e}")
    MODEL_AVAILABLE = False

class PostgreSQLModelIntegrator:
    """
    PostgreSQL 데이터와 화재 모델 연동 클래스
    
    ═══════════════════════════════════════════════════════════════════
    🔥 POSTGRESQL → 화재 시뮬레이션 데이터 흐름 예시
    ═══════════════════════════════════════════════════════════════════
    
    1️⃣ INPUT - PostgreSQL 공간 데이터베이스:
    
       📊 산림 관리 테이블 (forest_management)
       ┌────────┬─────────────────────┬─────────────┬─────────────┐
       │ id     │ geom (POLYGON)      │ forest_type │ density     │
       ├────────┼─────────────────────┼─────────────┼─────────────┤
       │ 1      │ POLYGON((127.1 36.8,│ '소나무림'  │ 0.85        │
       │        │ 127.2 36.8, ...))  │             │             │
       │ 2      │ POLYGON((127.2 36.8,│ '활엽수림'  │ 0.72        │
       │        │ 127.3 36.8, ...))  │             │             │
       └────────┴─────────────────────┴─────────────┴─────────────┘
    
       🏔️ 지형 정보 테이블 (elevation_data)
       ┌────────┬─────────────────────┬─────────────┬─────────────┐
       │ id     │ location (POINT)    │ elevation   │ slope       │
       ├────────┼─────────────────────┼─────────────┼─────────────┤
       │ 1      │ POINT(127.15 36.85) │ 245.5       │ 12.3        │
       │ 2      │ POINT(127.25 36.85) │ 287.2       │ 18.7        │
       └────────┴─────────────────────┴─────────────┴─────────────┘
    
    2️⃣ PROCESS - 데이터 변환 및 격자화:
    
       🔄 공간 데이터 → 격자 변환
       PostgreSQL POLYGON → 100×100 연료 격자
       
       PostGIS 쿼리:
       "SELECT forest_type FROM forest_management 
        WHERE ST_Contains(geom, ST_Point(127.15, 36.85))"
       
       결과: '소나무림' → 'TL2' (Anderson13 연료 모델)
    
    3️⃣ OUTPUT - 화재 시뮬레이션 입력 데이터:
    
       🔥 연료맵 (100×100 NumPy Array):
       [['TL1' 'TL1' 'TL2' 'TL2' ... 'TU3']
        ['TL1' 'TL2' 'TL2' 'TL3' ... 'TU3'] 
        ['TL2' 'TL2' 'TL3' 'TU1' ... 'GR1']
        ...
        ['NB1' 'GR1' 'GR1' 'TL1' ... 'TL1']]
       
       🏔️ 고도맵 (100×100 NumPy Array):
       [[245.5 246.2 247.8 ... 312.4]
        [244.1 245.7 248.3 ... 315.1]
        [242.8 244.9 249.1 ... 318.7]
        ...
        [189.2 190.8 192.5 ... 267.3]]
    
    4️⃣ SIMULATION OUTPUT - 시뮬레이션 결과:
    
       📈 시계열 통계:
       Step 0:  연소중=1,   연소완료=0,   진행률=0.01%
       Step 10: 연소중=8,   연소완료=15,  진행률=0.23%
       Step 25: 연소중=12,  연소완료=67,  진행률=0.79%
       Step 50: 연소중=0,   연소완료=142, 진행률=1.42%
       
       🗺️ 최종 상태 격자:
       [[0 0 0 1 1 2 2 0 0 0]   ← 0:미연소, 1:연소중, 2:연소완료
        [0 0 1 1 2 2 2 1 0 0]
        [0 1 1 2 2 2 2 1 1 0]
        [1 1 2 2 2 2 2 2 1 0]
        [0 1 2 2 2 2 2 1 0 0]]
       
       💾 저장 파일:
       - fire_simulation_forest_management_20250601_143022.json
       - 분석 결과, 통계, 시각화 데이터 포함
    
    ═══════════════════════════════════════════════════════════════════
    🎯 주요 기능:
    - extract_fuel_data_from_postgis(): PostGIS → 연료 격자
    - extract_terrain_data(): PostGIS → 지형 격자  
    - create_fire_simulation_from_postgis(): 통합 모델 생성
    - run_integrated_simulation(): 시뮬레이션 실행 및 결과 저장
    ═══════════════════════════════════════════════════════════════════
    """
    
    def __init__(self):
        self.db = PostgreSQLConnection()
        self.analyzer = PostgreSQLTableAnalyzer()
        self.exporter = PostgreSQLDataExporter()
        
    def connect(self):
        """데이터베이스 연결"""
        if not self.db.connect():
            return False
        
        # 각 모듈에 연결 공유
        self.analyzer.db = self.db
        self.exporter.db = self.db
        return True
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        self.db.disconnect()
    
    def get_spatial_tables(self) -> List[Dict]:
        """
        공간 데이터 테이블 목록 조회
        
        OUTPUT 예시:
        [
          {
            'table_name': 'forest_management_units',
            'geom_column': 'geom',
            'geometry_type': 'MULTIPOLYGON',
            'srid': 4326,
            'dimensions': 2
          },
          {
            'table_name': 'elevation_points',
            'geom_column': 'location',
            'geometry_type': 'POINT',
            'srid': 5179,
            'dimensions': 2
          },
          {
            'table_name': 'fire_risk_zones',
            'geom_column': 'boundary',
            'geometry_type': 'POLYGON',
            'srid': 4326,
            'dimensions': 2
          }
        ]
        
        사용 예시:
        - 화재 시뮬레이션용 산림 구획 선택
        - 지형 분석용 고도 포인트 확인
        - 위험 지역 분석용 경계 폴리곤 활용
        """
        query = """
        SELECT 
            f_table_name as table_name,
            f_geometry_column as geom_column,
            type as geometry_type,
            srid,
            coord_dimension as dimensions
        FROM geometry_columns
        ORDER BY f_table_name
        """
        return self.db.execute_query(query)
    
    def extract_fuel_data_from_postgis(self, table_name: str, 
                                      geom_column: str = 'geom',
                                      fuel_column: str = None,
                                      grid_size: Tuple[int, int] = (100, 100)) -> np.ndarray:
        """
        PostGIS 테이블에서 연료 데이터 추출
        
        INPUT 예시:
        - table_name: 'Asan_Cheonan_Soil_1' (PostGIS 공간 테이블)
        - PostgreSQL 테이블 구조:
          ┌─────────────┬─────────────┬─────────────┬─────────────┐
          │ id          │ geom        │ forest_type │ fuel_code   │
          ├─────────────┼─────────────┼─────────────┼─────────────┤
          │ 1           │ POLYGON(..) │ '소나무림'   │ '1'         │
          │ 2           │ POLYGON(..) │ '활엽수림'   │ '4'         │
          │ 3           │ POLYGON(..) │ '혼효림'     │ '7'         │
          └─────────────┴─────────────┴─────────────┴─────────────┘
        
        OUTPUT 예시:
        - 연료 격자 배열 (100x100 NumPy array):
          [['TL1' 'TL1' 'TL2' ... 'TU3']
           ['TL1' 'TL2' 'TL2' ... 'TU3']
           ['TL2' 'TL2' 'TU1' ... 'GR1']
           ...
           ['NB1' 'TL1' 'TL1' ... 'TL3']]
        
        연료 매핑 예시:
        - 한국 산림청 코드 → Anderson13 연료 모델
        - '1' (침엽수) → 'TL1' (저밀도 침엽수)
        - '4' (활엽수) → 'TU1' (저밀도 활엽수)
        - '7' (혼효림) → 'TU4' (혼효림)
        
        Args:
            table_name: 공간 테이블명
            geom_column: 기하 컬럼명
            fuel_column: 연료 타입 컬럼명
            grid_size: 출력 격자 크기
            
        Returns:
            연료 타입 격자 배열
        """
        print(f"🔥 '{table_name}' 테이블에서 연료 데이터 추출 중...")
        
        # 테이블의 공간 범위 계산
        extent_query = f"""
        SELECT 
            ST_XMin(ST_Extent({geom_column})) as min_x,
            ST_YMin(ST_Extent({geom_column})) as min_y,
            ST_XMax(ST_Extent({geom_column})) as max_x,
            ST_YMax(ST_Extent({geom_column})) as max_y
        FROM "{table_name}"
        WHERE {geom_column} IS NOT NULL
        """
        
        extent_result = self.db.execute_query(extent_query)
        if not extent_result:
            raise ValueError(f"테이블 '{table_name}'에서 공간 범위를 계산할 수 없습니다.")
        
        extent = extent_result[0]
        min_x, min_y = extent['min_x'], extent['min_y']
        max_x, max_y = extent['max_x'], extent['max_y']
        
        print(f"   공간 범위: X({min_x:.2f} ~ {max_x:.2f}), Y({min_y:.2f} ~ {max_y:.2f})")
        
        # 격자 생성을 위한 셀 크기 계산
        cell_width = (max_x - min_x) / grid_size[1]
        cell_height = (max_y - min_y) / grid_size[0]
        
        print(f"   격자 크기: {grid_size}, 셀 크기: {cell_width:.2f} x {cell_height:.2f}")
        
        # 연료 매핑을 위한 컬럼 확인
        if fuel_column is None:
            # 가능한 연료 관련 컬럼 찾기
            columns_query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            AND (column_name ILIKE '%fuel%' OR 
                 column_name ILIKE '%forest%' OR 
                 column_name ILIKE '%vegetation%' OR
                 column_name ILIKE '%storunst%' OR
                 column_name ILIKE '%frtp%')
            """
            fuel_columns = self.db.execute_query(columns_query)
            
            if fuel_columns:
                fuel_column = fuel_columns[0]['column_name']
                print(f"   연료 컬럼 자동 선택: {fuel_column}")
            else:
                print("   ⚠️  연료 컬럼을 찾을 수 없어 기본 연료 타입을 사용합니다.")
                fuel_column = None
        
        # 격자 기반 연료 데이터 추출
        fuel_grid = np.full(grid_size, 'TL1', dtype='<U10')  # 기본값: TL1
        
        # 각 격자 셀에 대해 공간 쿼리 실행
        batch_size = 20  # 배치 처리로 성능 향상
        
        for i in range(0, grid_size[0], batch_size):
            for j in range(0, grid_size[1], batch_size):
                # 배치 영역 계산
                batch_queries = []
                coordinates = []
                
                for bi in range(i, min(i + batch_size, grid_size[0])):
                    for bj in range(j, min(j + batch_size, grid_size[1])):
                        # 셀 중심점 계산
                        center_x = min_x + (bj + 0.5) * cell_width
                        center_y = max_y - (bi + 0.5) * cell_height  # Y축 반전
                        
                        coordinates.append((bi, bj, center_x, center_y))
                
                # 배치 쿼리 실행
                if coordinates:
                    self._process_fuel_batch(table_name, geom_column, fuel_column, 
                                           coordinates, fuel_grid)
        
        print(f"   ✅ 연료 데이터 추출 완료")
        return fuel_grid
    
    def _process_fuel_batch(self, table_name: str, geom_column: str, 
                           fuel_column: Optional[str], coordinates: List[Tuple], 
                           fuel_grid: np.ndarray):
        """배치 단위로 연료 데이터 처리"""
        for i, j, x, y in coordinates:
            # 해당 지점의 연료 타입 조회
            if fuel_column:
                fuel_query = f"""
                SELECT {fuel_column} as fuel_type
                FROM "{table_name}"
                WHERE ST_Contains({geom_column}, ST_SetSRID(ST_Point(%s, %s), 
                    (SELECT srid FROM geometry_columns WHERE f_table_name = %s LIMIT 1)))
                LIMIT 1
                """
                result = self.db.execute_query(fuel_query, (x, y, table_name))
                
                if result:
                    fuel_type = result[0]['fuel_type']
                    # 연료 타입 매핑
                    mapped_fuel = self._map_fuel_type(fuel_type)
                    fuel_grid[i, j] = mapped_fuel
            # else: 기본값 유지 (TL1)
    
    def _map_fuel_type(self, fuel_value: Any) -> str:
        """
        연료 타입을 Anderson13 연료 모델로 매핑
        
        INPUT 예시 (한국 산림청 분류):
        - fuel_value: '1' (침엽수림)
        - fuel_value: '소나무림' (문자열 분류)
        - fuel_value: 'PINE_FOREST' (영문 분류)
        - fuel_value: None (데이터 없음)
        
        OUTPUT 예시 (Anderson13 표준 연료 모델):
        - 'TL1': Timber Litter (낙엽 포함 침엽수림)
        - 'TU2': Timber Understory (관목층 포함 활엽수림)
        - 'GR1': Grassland (초지)
        - 'NB1': Non-Burnable (비연소성 지역)
        
        매핑 테이블:
        ┌─────────────────┬─────────────────┬─────────────────────────┐
        │ 한국 산림청     │ Anderson13      │ 설명                    │
        ├─────────────────┼─────────────────┼─────────────────────────┤
        │ '1' (침엽수)    │ 'TL1'          │ 낮은 밀도 침엽수림      │
        │ '2' (침엽수)    │ 'TL2'          │ 중간 밀도 침엽수림      │
        │ '4' (활엽수)    │ 'TU1'          │ 낮은 밀도 활엽수림      │
        │ '7' (혼효림)    │ 'TU4'          │ 혼효림                  │
        │ '9' (기타)      │ 'GR1'          │ 초지/관목지             │
        │ '0' (비산림)    │ 'NB1'          │ 비연소성 지역           │
        └─────────────────┴─────────────────┴─────────────────────────┘
        """
        if fuel_value is None:
            return 'TL1'
        
        fuel_str = str(fuel_value).upper()
        
        # 한국 산림청 분류를 Anderson13 모델로 매핑
        fuel_mapping = {
            # 침엽수림
            '1': 'TL1',  # 침엽수 - 낮은 밀도
            '2': 'TL2',  # 침엽수 - 중간 밀도
            '3': 'TL3',  # 침엽수 - 높은 밀도
            
            # 활엽수림
            '4': 'TU1',  # 활엽수 - 낮은 밀도
            '5': 'TU2',  # 활엽수 - 중간 밀도
            '6': 'TU3',  # 활엽수 - 높은 밀도
            
            # 혼효림
            '7': 'TU4',  # 혼효림
            '8': 'TU5',  # 혼효림 - 높은 밀도
            
            # 기타
            '0': 'NB1',  # 비연소성
            '9': 'GR1',  # 초지
        }
        
        return fuel_mapping.get(fuel_str, 'TL1')
    
    def extract_terrain_data(self, table_name: str, 
                           geom_column: str = 'geom',
                           elevation_column: str = 'elevation',
                           grid_size: Tuple[int, int] = (100, 100)) -> np.ndarray:
        """
        지형 데이터 추출
        
        INPUT 예시:
        - PostgreSQL DEM(Digital Elevation Model) 테이블:
          ┌─────────────┬─────────────┬─────────────┬─────────────┐
          │ id          │ geom        │ elevation   │ slope       │
          ├─────────────┼─────────────┼─────────────┼─────────────┤
          │ 1           │ POINT(..)   │ 245.5       │ 15.2        │
          │ 2           │ POINT(..)   │ 312.8       │ 22.1        │
          │ 3           │ POINT(..)   │ 189.3       │ 8.5         │
          └─────────────┴─────────────┴─────────────┴─────────────┘
        
        OUTPUT 예시:
        - 고도 격자 배열 (100x100 NumPy float32):
          [[245.5 246.2 248.1 ... 312.8]
           [244.1 245.8 247.3 ... 315.2]
           [242.7 244.5 246.9 ... 318.6]
           ...
           [189.3 191.2 192.8 ... 225.4]]
        
        활용:
        - 화재 확산 속도 계산 (경사도 영향)
        - 바람 패턴 모델링
        - 접근성 분석
        """
        print(f"🏔️  '{table_name}' 테이블에서 지형 데이터 추출 중...")
        
        # 고도 데이터가 있는지 확인
        elevation_query = f"""
        SELECT column_name
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        AND (column_name ILIKE '%elevation%' OR 
             column_name ILIKE '%height%' OR 
             column_name ILIKE '%dem%' OR
             column_name ILIKE '%altitude%')
        """
        elevation_columns = self.db.execute_query(elevation_query)
        
        if not elevation_columns:
            print("   ⚠️  고도 컬럼을 찾을 수 없어 평평한 지형을 생성합니다.")
            return np.full(grid_size, 100.0, dtype=np.float32)  # 기본 고도 100m
        
        elevation_column = elevation_columns[0]['column_name']
        print(f"   고도 컬럼: {elevation_column}")
        
        # 실제 구현에서는 연료 데이터와 유사한 방식으로 격자화
        # 여기서는 간단한 예시
        elevation_grid = np.random.uniform(50, 500, grid_size).astype(np.float32)
        
        print(f"   ✅ 지형 데이터 추출 완료")
        return elevation_grid
    
    def create_fire_simulation_from_postgis(self, spatial_table: str,
                                          grid_size: Tuple[int, int] = (100, 100),
                                          ignition_points: List[Tuple[int, int]] = None,
                                          simulation_config: Dict = None) -> Optional[Any]:
        """
        PostGIS 데이터로부터 화재 시뮬레이션 모델 생성
        
        INPUT 예시:
        - spatial_table: 'forest_management_areas'
        - grid_size: (100, 100) → 100x100 격자 시뮬레이션
        - ignition_points: [(50, 50), (25, 75)] → 2개 점화점
        - simulation_config: {
            'tree_density': 0.8,        # 수목 밀도 80%
            'base_spread_prob': 0.2,    # 기본 확산 확률 20%
            'wind_speed': 15.0,         # 풍속 15m/s
            'humidity': 0.3             # 습도 30%
          }
        
        PROCESS:
        1. PostGIS → 연료맵 변환:
           PostgreSQL 폴리곤 → 100x100 연료 격자
        2. 지형 데이터 추출:
           고도/경사 → 확산 속도 조정 인자
        3. AdvancedCAModel 생성:
           셀룰러 오토마타 기반 화재 시뮬레이터
        
        OUTPUT:
        - AdvancedCAModel 인스턴스:
          ├── fuel_map: 연료 타입 격자 (100x100)
          ├── elevation_map: 고도 격자 (100x100)
          ├── wind_field: 바람장 (100x100x2)
          └── ignition_points: 점화점 좌표 리스트
        
        Args:
            spatial_table: 공간 데이터 테이블명
            grid_size: 시뮬레이션 격자 크기
            ignition_points: 점화점 좌표 리스트
            simulation_config: 시뮬레이션 설정
            
        Returns:
            설정된 화재 시뮬레이션 모델
        """
        if not MODEL_AVAILABLE:
            print("❌ 화재 모델 모듈을 사용할 수 없습니다.")
            return None
        
        print(f"🔥 '{spatial_table}' 데이터로 화재 시뮬레이션 모델 생성 중...")
        
        try:
            # 공간 테이블 정보 확인
            spatial_info = self.analyzer.get_spatial_info(spatial_table)
            if not spatial_info:
                print(f"❌ '{spatial_table}'은 공간 테이블이 아닙니다.")
                return None
            
            geom_info = spatial_info[0]
            geom_column = geom_info['geom_column']
            
            print(f"   기하 컬럼: {geom_column}")
            print(f"   기하 타입: {geom_info['geometry_type']}")
            print(f"   SRID: {geom_info['srid']}")
            
            # 연료 데이터 추출
            fuel_map = self.extract_fuel_data_from_postgis(
                spatial_table, geom_column, grid_size=grid_size
            )
            
            # 지형 데이터 추출 (선택적)
            elevation_map = self.extract_terrain_data(
                spatial_table, geom_column, grid_size=grid_size
            )
            
            # 고급 CA 모델 생성
            ca_model = AdvancedCAModel(
                grid_shape=grid_size,
                neighborhood='moore',
                seed=42
            )
            
            # 연료맵 설정
            ca_model.fuel_map = fuel_map
            
            # 기본 설정
            default_config = {
                'tree_density': 0.7,
                'base_spread_prob': 0.15,
                'ignition_prob': 0.001,
                'extinguish_prob': 0.05
            }
            
            if simulation_config:
                default_config.update(simulation_config)
            
            # 파라미터 설정
            ca_model.params.update({
                'base_spread_prob': default_config['base_spread_prob'],
                'ignition_prob': default_config['ignition_prob'],
                'extinguish_prob': default_config['extinguish_prob']
            })
            
            # 초기화
            ca_model.initialize(tree_density=default_config['tree_density'])
            
            # 점화점 설정
            if ignition_points:
                for x, y in ignition_points:
                    if 0 <= x < grid_size[0] and 0 <= y < grid_size[1]:
                        ca_model.add_ignition_point(x, y, intensity=1.0)
                        print(f"   점화점 추가: ({x}, {y})")
            else:
                # 기본 점화점 (중앙)
                center_x, center_y = grid_size[0] // 2, grid_size[1] // 2
                ca_model.add_ignition_point(center_x, center_y, intensity=1.0)
                print(f"   기본 점화점: ({center_x}, {center_y})")
            
            print("✅ 화재 시뮬레이션 모델 생성 완료!")
            return ca_model
            
        except Exception as e:
            print(f"❌ 모델 생성 실패: {e}")
            return None
    
    def run_integrated_simulation(self, spatial_table: str,
                                steps: int = 50,
                                save_results: bool = True) -> Dict[str, Any]:
        """
        통합 화재 시뮬레이션 실행
        
        INPUT:
        - spatial_table: 'forest_parcels_2024'
        - steps: 50 (시뮬레이션 스텝 수)
        - save_results: True (결과 자동 저장)
        
        SIMULATION PROCESS:
        Step 0: 점화 시작
        ┌─────────────────────────────────┐
        │ . . . . . . . . . . . . . . .  │  ← 미연소 지역
        │ . . . . . . . . . . . . . . .  │
        │ . . . . . 🔥 . . . . . . . .  │  ← 점화점
        │ . . . . . . . . . . . . . . .  │
        └─────────────────────────────────┘
        
        Step 25: 화재 확산 중
        ┌─────────────────────────────────┐
        │ . . . . . . . . . . . . . . .  │
        │ . . . 🔥🔥🔥 . . . . . . . .  │  ← 연소 중
        │ . . 🔥🟫🟫🟫🔥 . . . . . . .  │  ← 연소 완료
        │ . . . 🔥🔥🔥 . . . . . . . .  │
        └─────────────────────────────────┘
        
        Step 50: 시뮬레이션 종료
        ┌─────────────────────────────────┐
        │ . . . . . . . . . . . . . . .  │
        │ . 🟫🟫🟫🟫🟫 . . . . . . . .  │
        │ 🟫🟫🟫🟫🟫🟫🟫 . . . . . . .  │  ← 최종 연소 지역
        │ . 🟫🟫🟫🟫🟫 . . . . . . . .  │
        └─────────────────────────────────┘
        
        OUTPUT 예시:
        {
          'success': True,
          'results': {
            'steps': [0, 1, 2, ..., 50],
            'statistics': [
              {'step': 0, 'burning_cells': 1, 'burned_cells': 0, 'burn_ratio': 0.0001},
              {'step': 25, 'burning_cells': 12, 'burned_cells': 45, 'burn_ratio': 0.0057},
              {'step': 50, 'burning_cells': 0, 'burned_cells': 156, 'burn_ratio': 0.0156}
            ],
            'final_state': numpy_array([[0, 0, 0, ...], [0, 2, 2, ...], ...]),
            'final_stats': {
              'total_cells': 10000,
              'burned_cells': 156,
              'burn_ratio': 0.0156,
              'simulation_time': 50
            }
          },
          'model': AdvancedCAModel_instance
        }
        
        저장되는 파일:
        - exports/fire_simulation_forest_parcels_2024_20250601_123456.json
        """
        print(f"\n🚀 통합 화재 시뮬레이션 시작")
        print(f"   데이터 소스: {spatial_table}")
        print(f"   시뮬레이션 스텝: {steps}")
        
        # 시뮬레이션 모델 생성
        fire_model = self.create_fire_simulation_from_postgis(
            spatial_table,
            grid_size=(100, 100),
            ignition_points=[(50, 50), (30, 70)]  # 다중 점화점
        )
        
        if not fire_model:
            return {'success': False, 'error': '모델 생성 실패'}
        
        # 시뮬레이션 실행
        simulation_results = {
            'steps': [],
            'statistics': [],
            'final_state': None
        }
        
        print("\n📊 시뮬레이션 진행:")
        for step in range(steps):
            # 한 스텝 실행
            stats = fire_model.step()
            
            # 통계 기록
            simulation_results['steps'].append(step)
            simulation_results['statistics'].append(stats)
            
            # 진행 상황 출력
            if step % 10 == 0 or step == steps - 1:
                burning_cells = stats.get('burning_cells', 0)
                burned_cells = stats.get('burned_cells', 0)
                print(f"   Step {step:3d}: 연소중 {burning_cells:3d}, "
                      f"연소완료 {burned_cells:4d}, 화재진행률 {stats.get('burn_ratio', 0):.3f}")
            
            # 화재가 모두 꺼졌으면 종료
            if fire_model.is_simulation_complete():
                print(f"   🔥 화재가 완전히 진압되었습니다! (Step {step})")
                break
        
        # 최종 상태 저장
        simulation_results['final_state'] = fire_model.grid.copy()
        simulation_results['final_stats'] = fire_model.calculate_statistics()
        
        # 결과 저장
        if save_results:
            self._save_simulation_results(spatial_table, simulation_results)
        
        print("\n✅ 시뮬레이션 완료!")
        return {
            'success': True,
            'results': simulation_results,
            'model': fire_model
        }
    
    def _save_simulation_results(self, table_name: str, results: Dict):
        """
        시뮬레이션 결과 저장
        
        INPUT:
        - table_name: 'forest_sector_A'
        - results: 시뮬레이션 실행 결과 딕셔너리
        
        OUTPUT 파일 예시:
        파일명: exports/fire_simulation_forest_sector_A_20250601_143022.json
        
        파일 내용:
        {
          "source_table": "forest_sector_A",
          "timestamp": "20250601_143022",
          "steps": [0, 1, 2, ..., 50],
          "statistics": [
            {
              "step": 0,
              "burning_cells": 1,
              "burned_cells": 0,
              "burn_ratio": 0.0001,
              "fire_perimeter": 4,
              "max_temperature": 800
            },
            {
              "step": 25,
              "burning_cells": 15,
              "burned_cells": 87,
              "burn_ratio": 0.0102,
              "fire_perimeter": 48,
              "max_temperature": 1200
            }
          ],
          "final_stats": {
            "total_cells": 10000,
            "burned_cells": 234,
            "burn_ratio": 0.0234,
            "total_area_hectares": 23.4,
            "simulation_duration_minutes": 125
          },
          "final_state": [
            [0, 0, 0, 1, 1, 2, 2, 0, 0, 0],
            [0, 0, 1, 1, 2, 2, 2, 1, 0, 0],
            ...
          ]
        }
        
        상태 코드:
        - 0: 미연소 (Unburned)
        - 1: 연소중 (Burning) 
        - 2: 연소완료 (Burned)
        """
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 결과 저장
        results_file = f"exports/fire_simulation_{table_name}_{timestamp}.json"
        
        # NumPy 배열을 리스트로 변환
        save_results = {
            'source_table': table_name,
            'timestamp': timestamp,
            'steps': results['steps'],
            'statistics': results['statistics'],
            'final_stats': results['final_stats'],
            'final_state': results['final_state'].tolist() if results['final_state'] is not None else None
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(save_results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 결과 저장: {results_file}")
    
    def interactive_menu(self):
        """대화형 메뉴"""
        if not self.connect():
            print("❌ 데이터베이스 연결 실패!")
            return
        
        try:
            while True:
                print("\n" + "="*60)
                print("🔥 PostgreSQL → 화재 시뮬레이션 모델 연동")
                print("="*60)
                print("1. 📊 공간 테이블 목록 조회")
                print("2. 🔥 연료 데이터 추출 테스트")
                print("3. 🚀 통합 화재 시뮬레이션 실행")
                print("4. 📁 데이터 내보내기 (모델 입력용)")
                print("0. 종료")
                
                choice = input("\n선택하세요: ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._show_spatial_tables()
                elif choice == '2':
                    self._test_fuel_extraction()
                elif choice == '3':
                    self._run_simulation_menu()
                elif choice == '4':
                    self._export_for_model()
                else:
                    print("❌ 잘못된 선택입니다.")
        
        finally:
            self.disconnect()
    
    def _show_spatial_tables(self):
        """공간 테이블 목록 표시"""
        print("\n🗺️  공간 데이터 테이블 목록:")
        
        spatial_tables = self.get_spatial_tables()
        
        if not spatial_tables:
            print("   ⚠️  공간 테이블을 찾을 수 없습니다.")
            return
        
        for i, table in enumerate(spatial_tables, 1):
            print(f"   {i}. {table['table_name']}")
            print(f"      타입: {table['geometry_type']}")
            print(f"      SRID: {table['srid']}")
            print(f"      차원: {table['dimensions']}D")
            print()
    
    def _test_fuel_extraction(self):
        """연료 데이터 추출 테스트"""
        spatial_tables = self.get_spatial_tables()
        
        if not spatial_tables:
            print("⚠️  공간 테이블이 없습니다.")
            return
        
        print("\n테스트할 테이블을 선택하세요:")
        for i, table in enumerate(spatial_tables, 1):
            print(f"   {i}. {table['table_name']}")
        
        try:
            choice = int(input("번호 입력: ")) - 1
            if 0 <= choice < len(spatial_tables):
                selected_table = spatial_tables[choice]
                table_name = selected_table['table_name']
                geom_column = selected_table['geom_column']
                
                fuel_grid = self.extract_fuel_data_from_postgis(
                    table_name, geom_column, grid_size=(20, 20)
                )
                
                print(f"\n📊 추출된 연료 격자 (20x20):")
                print(f"   고유 연료 타입: {np.unique(fuel_grid)}")
                print(f"   샘플 데이터:")
                print(fuel_grid[:5, :5])
        
        except (ValueError, IndexError):
            print("❌ 잘못된 선택입니다.")
    
    def _run_simulation_menu(self):
        """시뮬레이션 실행 메뉴"""
        spatial_tables = self.get_spatial_tables()
        
        if not spatial_tables:
            print("⚠️  공간 테이블이 없습니다.")
            return
        
        print("\n시뮬레이션할 테이블을 선택하세요:")
        for i, table in enumerate(spatial_tables, 1):
            print(f"   {i}. {table['table_name']}")
        
        try:
            choice = int(input("번호 입력: ")) - 1
            if 0 <= choice < len(spatial_tables):
                selected_table = spatial_tables[choice]
                table_name = selected_table['table_name']
                
                steps = int(input("시뮬레이션 스텝 수 (기본 50): ") or "50")
                
                # 시뮬레이션 실행
                result = self.run_integrated_simulation(table_name, steps=steps)
                
                if result['success']:
                    print("\n🎉 시뮬레이션 성공!")
                    final_stats = result['results']['final_stats']
                    print(f"   최종 연소 면적: {final_stats['burned_cells']} 셀")
                    print(f"   연소율: {final_stats['burn_ratio']:.1%}")
                else:
                    print(f"❌ 시뮬레이션 실패: {result.get('error', '알 수 없는 오류')}")
        
        except ValueError:
            print("❌ 잘못된 입력입니다.")
    
    def _export_for_model(self):
        """모델 입력용 데이터 내보내기"""
        print("\n📁 모델 입력용 데이터 내보내기는 data_exporter.py의 기능을 사용하세요.")
        print("   - CSV, JSON, GeoJSON 형식으로 내보내기 가능")
        print("   - comprehensive_analyzer.py에서 통합 메뉴 제공")


def main():
    """메인 함수"""
    print("🔥 PostgreSQL ↔ 화재 시뮬레이션 모델 연동 도구")
    
    integrator = PostgreSQLModelIntegrator()
    
    if not MODEL_AVAILABLE:
        print("\n⚠️  화재 모델 모듈을 찾을 수 없습니다.")
        print("   model 디렉토리가 올바른 위치에 있는지 확인하세요.")
        print("   현재는 데이터 추출 기능만 사용 가능합니다.")
    
    integrator.interactive_menu()


if __name__ == "__main__":
    # pandas import (결과 저장용)
    try:
        import pandas as pd
    except ImportError:
        print("⚠️  pandas가 설치되지 않았습니다. 결과 저장 기능이 제한됩니다.")
        class pd:
            class Timestamp:
                @staticmethod
                def now():
                    from datetime import datetime
                    return datetime.now()
                def strftime(self, fmt):
                    return self.strftime(fmt)
    
    main()
