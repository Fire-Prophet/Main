# 🔥 PostgreSQL 화재 시뮬레이션 모듈

PostgreSQL/PostGIS 공간 데이터베이스에서 산림, 토양, 지형 데이터를 추출하고 화재 시뮬레이션을 수행하는 모듈화된 시스템입니다.

## 📋 개요

이 모듈은 기존의 단일 파일 `model_integration.py`를 여러 개의 전문화된 모듈로 분리하여 재사용성과 유지보수성을 향상시켰습니다.

### 🔄 데이터 흐름
```
PostgreSQL/PostGIS → 공간 데이터 추출 → 격자 변환 → 화재 모델 → 시뮬레이션 결과
```

## 📁 모듈 구조

### 핵심 모듈

1. **`spatial_data_extractor.py`** 🗺️
   - PostgreSQL/PostGIS에서 공간 데이터 추출
   - 산림, 토양, 고도, 기상 데이터 추출
   - 경계 박스 기반 데이터 필터링

2. **`forest_data_processor.py`** 🌲
   - 산림 데이터를 Anderson 13 연료 모델로 변환
   - 한국 산림 유형 → 표준 연료 모델 매핑
   - 연료 밀도 및 위험도 계산

3. **`soil_data_processor.py`** 🏔️
   - 토양 데이터를 화재 위험 인자로 처리
   - 토양 수분, 유기물 함량 분석
   - 화재 위험 지수 계산

4. **`fire_simulation_connector.py`** 🔗
   - 처리된 데이터를 격자 형태로 변환
   - 벡터 → 래스터 변환
   - 화재 모델 호환 입력 데이터 생성

5. **`fire_model_integrator.py`** 🎯
   - 전체 파이프라인 통합 관리
   - 기존 화재 모델과 연동
   - 시뮬레이션 실행 및 결과 분석

## 🚀 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. PostgreSQL/PostGIS 설정
```sql
-- 데이터베이스 생성
CREATE DATABASE spatial_fire_db;

-- PostGIS 확장 활성화
CREATE EXTENSION postgis;

-- 필요한 테이블 (예시)
CREATE TABLE forest_management (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(POLYGON, 4326),
    forest_type VARCHAR(50),
    density FLOAT,
    fuel_code VARCHAR(10)
);

CREATE TABLE soil_management (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(POLYGON, 4326),
    soil_type VARCHAR(50),
    moisture_content FLOAT,
    organic_matter FLOAT,
    drainage INTEGER,
    fire_risk_index FLOAT
);
```

## 📖 사용법

### 기본 사용법

```python
from postgreSQLmodule import FireModelIntegrator

# 데이터베이스 설정
db_config = {
    'host': 'localhost',
    'database': 'spatial_fire_db',
    'user': 'postgres',
    'password': 'your_password',
    'port': 5432
}

# 시뮬레이션 설정
simulation_config = {
    'grid_size': [100, 100],
    'simulation_steps': 100,
    'model_type': 'integrated',
    'wind_speed': 5.0,
    'wind_direction': 0.0,
    'temperature': 25.0,
    'humidity': 50.0
}

# 통합기 생성
integrator = FireModelIntegrator(db_config, simulation_config)

# 시뮬레이션 실행
bounding_box = (127.0, 37.0, 127.5, 37.5)  # (min_lng, min_lat, max_lng, max_lat)
ignition_points = [(127.2, 37.2)]  # 발화점 (경도, 위도)

results = integrator.run_full_simulation(
    bounding_box=bounding_box,
    ignition_points=ignition_points
)

print(f"연소 면적: {results['analysis']['summary']['burned_area_ha']:.2f} ha")
print(f"연소율: {results['analysis']['summary']['burn_percentage']:.1f}%")
```

### 개별 모듈 사용법

#### 1. 데이터 추출만 수행
```python
from postgreSQLmodule import SpatialDataExtractor

extractor = SpatialDataExtractor(db_config)
if extractor.connect():
    data = extractor.extract_all_fire_simulation_data(bounding_box)
    extractor.save_extracted_data(data, "my_fire_data")
    extractor.disconnect()
```

#### 2. 산림 데이터 처리
```python
from postgreSQLmodule import ForestDataProcessor

processor = ForestDataProcessor()
forest_data = processor.process_forest_data(raw_forest_data)
fuel_grid = processor.create_fuel_grid(forest_data, grid_size=(100, 100))
```

#### 3. 시뮬레이션 입력 데이터만 생성
```python
from postgreSQLmodule import FireSimulationConnector

connector = FireSimulationConnector(grid_size=(100, 100))
simulation_input = connector.create_simulation_input(
    forest_data, soil_data, elevation_data, weather_data, bounding_box
)
connector.save_simulation_input(simulation_input, "sim_input.npz")
```

## 🔧 설정 옵션

### 시뮬레이션 설정
```python
simulation_config = {
    'grid_size': [100, 100],           # 격자 크기 [rows, cols]
    'grid_resolution': 0.001,          # 격자 해상도 (도 단위)
    'simulation_steps': 100,           # 최대 시뮬레이션 단계
    'time_step': 1.0,                  # 시간 단계 (분)
    'model_type': 'integrated',        # 모델 타입
    'wind_speed': 5.0,                 # 풍속 (m/s)
    'wind_direction': 0.0,             # 풍향 (도)
    'temperature': 25.0,               # 온도 (°C)
    'humidity': 50.0,                  # 습도 (%)
    'output_dir': 'fire_results'       # 결과 저장 디렉토리
}
```

### 화재 모델 타입
- `'integrated'`: 통합 화재 시뮬레이션 (권장)
- `'advanced_ca'`: 고급 셀룰러 오토마타 모델
- `'realistic'`: 현실적 화재 모델

## 📊 출력 데이터

### 시뮬레이션 결과 구조
```python
results = {
    'metadata': {
        'bounding_box': (127.0, 37.0, 127.5, 37.5),
        'simulation_time': '2024-01-01T12:00:00',
        'grid_size': [100, 100],
        'total_steps': 45,
        'ignition_points': [(50, 50)]
    },
    'analysis': {
        'summary': {
            'burned_area_ha': 125.6,
            'burn_percentage': 12.56,
            'simulation_steps': 45
        },
        'temporal_progression': [...],
        'fuel_impact': {...},
        'spatial_analysis': {...}
    },
    'simulation_results': {...}
}
```

### 저장 파일
- `fire_simulation_results_YYYYMMDD_HHMMSS.json`: 주요 결과 및 분석
- `fire_simulation_arrays_YYYYMMDD_HHMMSS.npz`: NumPy 배열 데이터
- `fire_simulation_data/`: 추출된 원본 데이터

## 🔍 고급 기능

### 1. 사용자 정의 연료 모델
```python
# 산림 처리기에 새로운 연료 모델 추가
processor = ForestDataProcessor()
processor.add_custom_fuel_mapping('특수소나무림', 'TL4')
```

### 2. 기상 조건 오버라이드
```python
weather_override = {
    'wind_speed': 15.0,    # 강풍 시나리오
    'humidity': 20.0,      # 건조 조건
    'temperature': 35.0    # 고온 조건
}

results = integrator.run_full_simulation(
    bounding_box=bounding_box,
    weather_override=weather_override
)
```

### 3. 다중 발화점 시뮬레이션
```python
ignition_points = [
    (127.1, 37.1),  # 첫 번째 발화점
    (127.3, 37.3),  # 두 번째 발화점
    (127.2, 37.4)   # 세 번째 발화점
]
```

## 🧪 테스트

### 단위 테스트 실행
```bash
# 개별 모듈 테스트
python -m postgreSQLmodule.spatial_data_extractor
python -m postgreSQLmodule.forest_data_processor
python -m postgreSQLmodule.soil_data_processor
python -m postgreSQLmodule.fire_simulation_connector
python -m postgreSQLmodule.fire_model_integrator

# 전체 파이프라인 테스트
python test_integration.py
```

## 📈 성능 최적화

### 1. 격자 크기 최적화
- 소규모 지역: 50×50 또는 100×100
- 대규모 지역: 200×200 또는 500×500
- 메모리 사용량과 정확도의 균형 고려

### 2. 데이터베이스 최적화
- 공간 인덱스 생성: `CREATE INDEX ON forest_management USING GIST(geom);`
- 통계 업데이트: `ANALYZE forest_management;`

### 3. 병렬 처리
```python
# 다중 시나리오 병렬 실행 (추후 구현 예정)
scenarios = [
    {'wind_speed': 5.0, 'humidity': 30.0},
    {'wind_speed': 10.0, 'humidity': 20.0},
    {'wind_speed': 15.0, 'humidity': 10.0}
]
```

## 🔧 문제 해결

### 일반적인 문제들

1. **PostgreSQL 연결 실패**
   ```
   ❌ PostgreSQL 연결 실패: FATAL: password authentication failed
   ```
   - 데이터베이스 자격 증명 확인
   - PostgreSQL 서비스 상태 확인
   - `pg_hba.conf` 설정 확인

2. **화재 모델 모듈 없음**
   ```
   ⚠️ 화재 모델을 가져올 수 없습니다: No module named 'advanced_ca_model'
   ```
   - `../model/` 디렉토리에 화재 모델 파일 확인
   - 더미 모드로 기본 시뮬레이션 실행

3. **메모리 부족**
   ```
   MemoryError: Unable to allocate array
   ```
   - 격자 크기 축소 (`grid_size` 조정)
   - 시뮬레이션 단계 수 감소

## 🤝 기여 방법

1. 새로운 연료 모델 추가
2. 기상 모델 통합 개선
3. 공간 데이터 처리 최적화
4. 시각화 기능 추가
5. 단위 테스트 확장

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 기능 요청이 있으시면 이슈를 등록해 주세요.

---

**🔥 PostgreSQL 화재 시뮬레이션 모듈로 현실적인 화재 확산 시뮬레이션을 경험해보세요!**
