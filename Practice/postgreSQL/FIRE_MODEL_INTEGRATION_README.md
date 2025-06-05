# 🔥 PostgreSQL ↔ 화재 시뮬레이션 모델 통합 시스템

PostgreSQL 공간 데이터베이스와 화재 시뮬레이션 모델을 연동하는 통합 시스템입니다. 실제 지리공간 데이터를 기반으로 화재 확산 시뮬레이션을 수행할 수 있습니다.

## 🎯 시스템 개요

이 통합 시스템은 PostGIS 공간 데이터를 추출하여 화재 시뮬레이션 모델의 입력 데이터로 변환하고, 실제 지형과 연료 분포를 반영한 현실적인 화재 확산 시뮬레이션을 제공합니다.

### 🔄 데이터 흐름

```
PostgreSQL/PostGIS → 공간 데이터 추출 → 격자 변환 → 화재 모델 → 시뮬레이션 결과
```

## 📁 파일 구조

### 🔥 통합 모듈
- `model_integration.py`: **핵심 통합 모듈** - PostgreSQL과 화재 모델 연동
- `integration_examples.py`: 통합 시스템 사용 예제 및 대화형 메뉴

### 🗄️ 기존 PostgreSQL 모듈
- `db_connection.py`: PostgreSQL 연결 관리
- `table_analyzer.py`: 테이블 분석 도구
- `data_exporter.py`: 데이터 내보내기 도구
- `comprehensive_analyzer.py`: 종합 분석 인터페이스

### 📂 출력 디렉토리
- `exports/`: 시뮬레이션 결과 및 내보낸 데이터 저장

## 🚀 주요 기능

### 1️⃣ 공간 데이터 추출 및 변환

#### 📊 INPUT - PostgreSQL 공간 테이블
```sql
-- 산림 관리 테이블 예시
CREATE TABLE forest_management (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(POLYGON, 4326),
    forest_type VARCHAR(50),    -- '소나무림', '활엽수림', '혼효림'
    density FLOAT,              -- 수목 밀도 (0.0-1.0)
    fuel_code VARCHAR(10)       -- 연료 분류 코드 ('1', '2', '4', '7', etc.)
);

-- 지형 정보 테이블 예시
CREATE TABLE elevation_data (
    id SERIAL PRIMARY KEY,
    location GEOMETRY(POINT, 4326),
    elevation FLOAT,            -- 고도 (미터)
    slope FLOAT                 -- 경사도 (도)
);
```

#### 🔄 PROCESS - 데이터 변환
- **공간 쿼리**: PostGIS 함수로 폴리곤 → 격자 변환
- **연료 매핑**: 한국 산림청 분류 → Anderson13 연료 모델
- **격자화**: 연속 공간 데이터 → 시뮬레이션 격자 배열

#### 📈 OUTPUT - 시뮬레이션 입력 데이터
```python
# 연료맵 (100×100 NumPy Array)
fuel_map = [
    ['TL1', 'TL1', 'TL2', 'TL2', ..., 'TU3'],
    ['TL1', 'TL2', 'TL2', 'TL3', ..., 'TU3'], 
    ['TL2', 'TL2', 'TL3', 'TU1', ..., 'GR1'],
    ...
]

# 고도맵 (100×100 NumPy Array)
elevation_map = [
    [245.5, 246.2, 247.8, ..., 312.4],
    [244.1, 245.7, 248.3, ..., 315.1],
    [242.8, 244.9, 249.1, ..., 318.7],
    ...
]
```

### 2️⃣ 연료 타입 매핑 시스템

#### 🌲 한국 산림청 분류 → Anderson13 연료 모델

| 한국 산림청 | Anderson13 | 설명 |
|-------------|------------|------|
| `'1'` (침엽수) | `'TL1'` | 저밀도 침엽수림 |
| `'2'` (침엽수) | `'TL2'` | 중간밀도 침엽수림 |
| `'3'` (침엽수) | `'TL3'` | 고밀도 침엽수림 |
| `'4'` (활엽수) | `'TU1'` | 저밀도 활엽수림 |
| `'5'` (활엽수) | `'TU2'` | 중간밀도 활엽수림 |
| `'6'` (활엽수) | `'TU3'` | 고밀도 활엽수림 |
| `'7'` (혼효림) | `'TU4'` | 혼효림 |
| `'8'` (혼효림) | `'TU5'` | 고밀도 혼효림 |
| `'9'` (기타) | `'GR1'` | 초지/관목지 |
| `'0'` (비산림) | `'NB1'` | 비연소성 지역 |

### 3️⃣ 화재 시뮬레이션 실행

#### 🎮 시뮬레이션 설정
```python
simulation_config = {
    'grid_size': (100, 100),           # 격자 크기
    'ignition_points': [(50, 50), (25, 75)],  # 점화점 좌표
    'tree_density': 0.8,               # 수목 밀도 80%
    'base_spread_prob': 0.2,           # 기본 확산 확률 20%
    'wind_speed': 15.0,                # 풍속 15m/s
    'humidity': 0.3,                   # 습도 30%
    'steps': 50                        # 시뮬레이션 스텝
}
```

#### 🔥 시뮬레이션 진행 과정

**Step 0: 점화 시작**
```
┌─────────────────────────────────┐
│ . . . . . . . . . . . . . . .  │  ← 미연소 지역
│ . . . . . . . . . . . . . . .  │
│ . . . . . 🔥 . . . . . . . .  │  ← 점화점
│ . . . . . . . . . . . . . . .  │
└─────────────────────────────────┘
```

**Step 25: 화재 확산 중**
```
┌─────────────────────────────────┐
│ . . . . . . . . . . . . . . .  │
│ . . . 🔥🔥🔥 . . . . . . . .  │  ← 연소 중
│ . . 🔥🟫🟫🟫🔥 . . . . . . .  │  ← 연소 완료
│ . . . 🔥🔥🔥 . . . . . . . .  │
└─────────────────────────────────┘
```

**Step 50: 시뮬레이션 종료**
```
┌─────────────────────────────────┐
│ . . . . . . . . . . . . . . .  │
│ . 🟫🟫🟫🟫🟫 . . . . . . . .  │
│ 🟫🟫🟫🟫🟫🟫🟫 . . . . . . .  │  ← 최종 연소 지역
│ . 🟫🟫🟫🟫🟫 . . . . . . . .  │
└─────────────────────────────────┘
```

### 4️⃣ 시뮬레이션 결과 분석

#### 📊 시계열 통계
```
Step   0: 연소중=  1, 연소완료=  0, 화재진행률= 0.01%
Step  10: 연소중=  8, 연소완료= 15, 화재진행률= 0.23%
Step  25: 연소중= 12, 연소완료= 67, 화재진행률= 0.79%
Step  50: 연소중=  0, 연소완료=142, 화재진행률= 1.42%
```

#### 💾 결과 파일 (JSON 형식)
```json
{
  "source_table": "forest_management_sector_A",
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
```

**상태 코드:**
- `0`: 미연소 (Unburned)
- `1`: 연소중 (Burning) 
- `2`: 연소완료 (Burned)

## 📦 설치 및 설정

### 1. 의존성 설치

```bash
# PostgreSQL 관련 패키지
pip install psycopg2-binary pandas numpy

# 화재 모델 의존성 (model 디렉토리에서)
cd ../model
pip install -r requirements.txt
```

### 2. 데이터베이스 설정

```bash
# 환경변수 설정 (선택사항)
cp .env.template .env
# .env 파일 편집하여 PostgreSQL 비밀번호 설정
```

**데이터베이스 연결 정보:**
- **호스트**: 123.212.210.230
- **포트**: 5432
- **사용자**: postgres
- **데이터베이스**: gis_db
- **PostGIS 확장**: 필수

## 🔧 사용법

### 🚀 빠른 시작 (대화형 메뉴)

```bash
python integration_examples.py
```

**메뉴 옵션:**
1. **기본 연동 테스트**: PostgreSQL → 화재 모델 연동 확인
2. **데이터 내보내기**: CSV, JSON, GeoJSON 형식으로 내보내기
3. **사용자 정의 연료 매핑**: 커스텀 연료 분류 적용
4. **실제 데이터 시뮬레이션**: 대규모 시뮬레이션 실행
5. **데이터 전처리**: 품질 검사 및 전처리
6. **전체 통합 인터페이스**: 종합 분석 도구

### 💻 프로그래밍 방식 사용

#### 1. 기본 연동 테스트

```python
from model_integration import PostgreSQLModelIntegrator

# 통합기 생성 및 연결
integrator = PostgreSQLModelIntegrator()
if integrator.connect():
    
    # 공간 테이블 목록 조회
    spatial_tables = integrator.get_spatial_tables()
    print("공간 테이블:", spatial_tables)
    
    # 연료 데이터 추출
    fuel_grid = integrator.extract_fuel_data_from_postgis(
        'forest_parcels', 
        grid_size=(50, 50)
    )
    print("연료 격자 크기:", fuel_grid.shape)
    
    integrator.disconnect()
```

#### 2. 화재 시뮬레이션 모델 생성

```python
# 화재 시뮬레이션 모델 생성
fire_model = integrator.create_fire_simulation_from_postgis(
    spatial_table='forest_management_units',
    grid_size=(100, 100),
    ignition_points=[(50, 50), (25, 75)],
    simulation_config={
        'tree_density': 0.8,
        'base_spread_prob': 0.2,
        'wind_speed': 15.0
    }
)

if fire_model:
    print("✅ 화재 모델 생성 성공!")
    print(f"격자 크기: {fire_model.grid.shape}")
    print(f"연료 타입: {np.unique(fire_model.fuel_map)}")
```

#### 3. 통합 시뮬레이션 실행

```python
# 전체 시뮬레이션 파이프라인 실행
result = integrator.run_integrated_simulation(
    spatial_table='forest_risk_zones',
    steps=100,
    save_results=True
)

if result['success']:
    stats = result['results']['final_stats']
    print(f"🔥 시뮬레이션 완료!")
    print(f"   연소 면적: {stats['burned_cells']} 셀")
    print(f"   연소율: {stats['burn_ratio']:.1%}")
    print(f"   결과 파일: exports/fire_simulation_*.json")
```

#### 4. 사용자 정의 연료 매핑

```python
# 커스텀 연료 매핑 함수
def custom_fuel_mapping(fuel_value):
    """사용자 정의 연료 매핑"""
    custom_map = {
        'PINE_FOREST': 'TL2',
        '소나무림': 'TL2',
        'OAK_FOREST': 'TU2',
        'MIXED_FOREST': 'TU3',
        'GRASSLAND': 'GR1',
        'URBAN': 'NB1'
    }
    return custom_map.get(str(fuel_value), 'TL1')

# 연료 매핑 함수 교체
integrator._map_fuel_type = custom_fuel_mapping
```

#### 5. 고급 분석 및 내보내기

```python
from data_exporter import PostgreSQLDataExporter

exporter = PostgreSQLDataExporter()
if exporter.connect():
    
    # CSV로 내보내기 (모델 입력용)
    exporter.export_table_to_csv(
        'forest_management', 
        limit=10000,
        filename='forest_data_for_simulation.csv'
    )
    
    # GeoJSON으로 공간 데이터 내보내기
    exporter.export_spatial_data_to_geojson(
        'fire_risk_zones',
        'geom',
        filename='fire_risk_areas.geojson'
    )
    
    exporter.disconnect()
```

## 🎯 활용 시나리오

### 🌲 1. 산림 화재 위험도 평가
```python
# 실제 산림 데이터 기반 위험도 평가
risk_simulation = integrator.run_integrated_simulation(
    spatial_table='national_forest_inventory',
    steps=200,
    save_results=True
)
```

### 🚁 2. 화재 진압 계획 수립
```python
# 다중 점화점 시나리오 분석
suppression_plan = integrator.create_fire_simulation_from_postgis(
    spatial_table='fire_suppression_zones',
    ignition_points=[(30, 40), (70, 60), (50, 80)],  # 최악 시나리오
    simulation_config={
        'wind_speed': 25.0,  # 강풍 조건
        'humidity': 0.2      # 건조 조건
    }
)
```

### 🌪️ 3. 기상 조건 변화 시뮬레이션
```python
# 풍속별 화재 확산 비교
wind_scenarios = [5.0, 15.0, 25.0, 35.0]
results = []

for wind_speed in wind_scenarios:
    result = integrator.run_integrated_simulation(
        spatial_table='weather_analysis_area',
        simulation_config={'wind_speed': wind_speed},
        steps=100
    )
    results.append(result)
```

### 🛡️ 4. 방화선 효과 검증
```python
# 방화선이 있는 지역과 없는 지역 비교
# (NB1 연료 타입으로 방화선 표현)
firebreak_effectiveness = integrator.run_integrated_simulation(
    spatial_table='firebreak_test_area',
    steps=150
)
```

## 📈 성능 및 확장성

### ⚡ 성능 최적화
- **배치 처리**: 20개 셀 단위로 공간 쿼리 배치 실행
- **격자 크기 조정**: 큰 영역은 낮은 해상도로 시작
- **인덱스 활용**: PostGIS 공간 인덱스 최적화

### 🔧 확장 가능성
- **다양한 연료 모델**: FARSITE, FlamMap 호환 모델 추가
- **실시간 데이터 연동**: 기상 관측소, 위성 데이터 통합
- **3D 시뮬레이션**: 수관층 화재 모델링
- **GPU 가속**: CUDA 기반 대규모 시뮬레이션

## 🗂️ 출력 파일 형식

### 📊 시뮬레이션 결과 파일
```
exports/
├── fire_simulation_{table_name}_{timestamp}.json    # 시뮬레이션 결과
├── {table_name}_{timestamp}.csv                     # 원본 데이터 (CSV)
├── {table_name}_{timestamp}.geojson                 # 공간 데이터 (GeoJSON)
└── fuel_mapping_report_{timestamp}.txt              # 연료 매핑 보고서
```

### 📋 분석 보고서
```
exports/
├── {table_name}_analysis_{timestamp}.txt            # 텍스트 분석 보고서
├── {table_name}_quality_{timestamp}.json            # 데이터 품질 보고서
└── simulation_summary_{timestamp}.html              # HTML 시각화 보고서
```

## 🔍 문제 해결

### ❌ 일반적인 오류

#### 1. 데이터베이스 연결 실패
```bash
# 방화벽 확인
telnet 123.212.210.230 5432

# PostgreSQL 상태 확인
pg_isready -h 123.212.210.230 -p 5432
```

#### 2. PostGIS 확장 오류
```sql
-- PostGIS 설치 확인
SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis');

-- 공간 테이블 확인
SELECT * FROM geometry_columns LIMIT 5;
```

#### 3. 메모리 부족 오류
```python
# 격자 크기 줄이기
fuel_grid = integrator.extract_fuel_data_from_postgis(
    'large_table', 
    grid_size=(50, 50)  # 100x100 대신 50x50 사용
)

# 배치 크기 조정
integrator.batch_size = 10  # 기본값 20에서 10으로 감소
```

#### 4. 연료 매핑 오류
```python
# 사용자 정의 매핑으로 오류 해결
def safe_fuel_mapping(fuel_value):
    try:
        return custom_mapping[fuel_value]
    except (KeyError, TypeError):
        return 'TL1'  # 안전한 기본값
```

### 🛠️ 디버깅 모드

```python
import logging

# 상세 로그 활성화
logging.basicConfig(level=logging.DEBUG)

# 연결 테스트
integrator = PostgreSQLModelIntegrator()
success = integrator.connect()
print(f"연결 상태: {'성공' if success else '실패'}")
```

## 📚 참고 자료

### 🔗 관련 문서
- **PostgreSQL 공식 문서**: https://www.postgresql.org/docs/
- **PostGIS 매뉴얼**: https://postgis.net/documentation/
- **Anderson13 연료 모델**: USFS Fire Behavior Research
- **화재 시뮬레이션 이론**: Rothermel Fire Spread Model

### 📖 코드 구조
```
model_integration.py
├── PostgreSQLModelIntegrator 클래스
│   ├── connect() / disconnect()              # 데이터베이스 연결 관리
│   ├── get_spatial_tables()                  # 공간 테이블 목록
│   ├── extract_fuel_data_from_postgis()      # 연료 데이터 추출
│   ├── extract_terrain_data()                # 지형 데이터 추출
│   ├── create_fire_simulation_from_postgis() # 화재 모델 생성
│   ├── run_integrated_simulation()           # 통합 시뮬레이션 실행
│   └── interactive_menu()                    # 대화형 인터페이스
```

### 🧪 테스트 데이터
```sql
-- 테스트용 샘플 데이터 생성
INSERT INTO test_forest_area (geom, forest_type, fuel_code) VALUES
(ST_GeomFromText('POLYGON((127.0 36.8, 127.1 36.8, 127.1 36.9, 127.0 36.9, 127.0 36.8))', 4326), '소나무림', '2'),
(ST_GeomFromText('POLYGON((127.1 36.8, 127.2 36.8, 127.2 36.9, 127.1 36.9, 127.1 36.8))', 4326), '활엽수림', '5'),
(ST_GeomFromText('POLYGON((127.0 36.9, 127.1 36.9, 127.1 37.0, 127.0 37.0, 127.0 36.9))', 4326), '혼효림', '7');
```

## 📞 지원 및 기여

### 🐛 버그 리포트
이슈나 버그를 발견하면 다음 정보와 함께 리포트해주세요:
- PostgreSQL 버전
- PostGIS 버전
- Python 버전
- 오류 메시지
- 재현 가능한 단계

### 🚀 기능 요청
새로운 기능이나 개선사항 제안을 환영합니다:
- 새로운 연료 모델 지원
- 추가 데이터 형식 지원
- 성능 개선
- 사용자 인터페이스 개선

### 🤝 기여 방법
1. Fork 및 Clone
2. 기능 브랜치 생성
3. 테스트 코드 작성
4. Pull Request 제출

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 학습, 연구, 상업적 목적으로 자유롭게 사용할 수 있습니다.

## 🙏 감사의 말

- **PostgreSQL 커뮤니티**: 강력한 오픈소스 데이터베이스
- **PostGIS 프로젝트**: 뛰어난 공간 데이터 확장
- **NumPy/SciPy 생태계**: 과학 컴퓨팅 라이브러리
- **화재 연구 커뮤니티**: Anderson13 연료 모델 및 화재 행동 연구

---

**🔥 PostgreSQL과 화재 시뮬레이션의 완벽한 결합!**

실제 지리공간 데이터를 활용한 현실적인 화재 시뮬레이션으로 더 나은 화재 예방과 대응 계획을 수립하세요.
