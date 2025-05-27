# 한국 산림 화재 확산 시뮬레이션 - 모델 검증 및 현실성 향상 가이드

## 📋 목차
1. [개요](#개요)
2. [새로운 기능](#새로운-기능)
3. [설치 및 설정](#설치-및-설정)
4. [모델 검증 시스템](#모델-검증-시스템)
5. [현실성 향상 모듈](#현실성-향상-모듈)
6. [통합 시스템 사용법](#통합-시스템-사용법)
7. [결과 해석 가이드](#결과-해석-가이드)
8. [문제 해결](#문제-해결)

## 🎯 개요

본 시스템은 한국 산림 데이터를 Anderson 13 연료모델로 매핑하고, 셀룰러 오토마타(CA) 기반 화재 확산 시뮬레이션을 수행하는 종합적인 도구입니다. 이번 업데이트에서는 **모델 검증 분석**과 **현실성 향상** 기능이 추가되어 더욱 정확하고 신뢰할 수 있는 시뮬레이션이 가능합니다.

### 주요 특징
- ✅ 종합적인 모델 검증 및 성능 평가
- 🔥 현실적인 화재 행동 모델링 (비화, 화재 강도, 진압 활동 등)
- 📊 자동화된 분석 및 보고서 생성
- 🎨 고급 시각화 및 애니메이션
- ⚡ 성능 최적화 및 실시간 모니터링

## 🆕 새로운 기능

### 1. 모델 검증 시스템 (`model_validation.py`)
- **확산 패턴 검증**: 컴팩트성, 원형성, 프랙탈 차원 분석
- **시간적 진행 검증**: 연소율, 둘레 성장, 가속 구간 분석
- **연료별 반응 검증**: 연료 타입별 연소 특성 분석
- **통계적 검증**: 혼동 행렬, ROC 곡선, 분류 성능 지표
- **실제 데이터와의 비교**: Jaccard 유사도, 면적 오차 분석

### 2. 현실성 향상 모듈 (`realistic_fire_model.py`)
- **비화(Spotting) 현상**: 바람에 의한 불씨 이동 및 원거리 착화
- **화재 행동 분류**: 표면화재, 수관화재, 지중화재, 불꽃폭풍
- **상세한 화재 특성**: 화재 강도, 화염 길이, 열 유속 계산
- **인간 활동 영향**: 도로, 전력선, 레크리에이션 지역의 착화 위험
- **진압 활동 시뮬레이션**: 지상 소방대, 항공 살수, 방화선
- **계절/시간대별 효과**: 자연적인 화재 위험도 변화

### 3. 통합 시스템 (`integrated_validation_system.py`)
- **실시간 성능 모니터링**: 시뮬레이션 중 지속적인 검증
- **자동 개선 제안**: AI 기반 모델 파라미터 조정 권고
- **종합 보고서**: JSON, 마크다운, 시각화를 포함한 완전한 분석 보고서
- **애니메이션 생성**: 화재 확산 과정의 동적 시각화

## 🔧 설치 및 설정

### 1. 환경 준비
```bash
# Python 3.8 이상 필요
python --version

# 가상환경 생성 (권장)
python -m venv fire_simulation_env
source fire_simulation_env/bin/activate  # Linux/Mac
# fire_simulation_env\Scripts\activate  # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 추가 의존성 (선택사항)
```bash
# 애니메이션 생성을 위한 추가 패키지
pip install ffmpeg-python

# GPU 가속을 위한 CUDA (NVIDIA GPU가 있는 경우)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 🔍 모델 검증 시스템

### 기본 사용법

```python
from model_validation import ModelValidator, load_simulation_results

# 시뮬레이션 결과 로드
results = load_simulation_results("simulation_output_directory")

# 검증기 생성
validator = ModelValidator(results)

# 각종 검증 수행
pattern_metrics = validator.validate_spread_pattern()
temporal_metrics = validator.validate_temporal_progression() 
fuel_metrics = validator.validate_fuel_response()

# 보고서 생성
report_path = validator.generate_validation_report("validation_results")
```

### 실제 데이터와의 비교

```python
import numpy as np

# 실제 화재 데이터 (0: 연소안됨, 1: 연소됨)
actual_burned_area = np.load("actual_fire_data.npy")

# 검증기에 실제 데이터 제공
validator = ModelValidator(results, actual_burned_area)

# 정확도 분석
confusion_metrics = validator.calculate_confusion_matrix(actual_burned_area)
roc_metrics = validator.calculate_roc_metrics(actual_burned_area)

print(f"정확도: {confusion_metrics['accuracy']:.3f}")
print(f"F1 점수: {confusion_metrics['f1_score']:.3f}")
print(f"AUC: {roc_metrics['auc']:.3f}")
```

### 검증 지표 해석

#### 1. 확산 패턴 지표
- **컴팩트성 (Compactness)**: 0.7 이상이면 양호한 집중적 확산
- **원형성 (Circularity)**: 0.6 이상이면 자연스러운 원형 확산
- **프랙탈 차원**: 1.2-1.8이면 적절한 복잡성

#### 2. 시간적 진행 지표
- **성장 일관성**: 0.7 이상이면 안정적인 확산
- **가속 구간**: 2-4개 구간이 자연스러움
- **평균 연소율**: 연료 타입별 기대값과 비교

#### 3. 분류 성능 지표
- **정확도**: 0.8 이상 목표
- **F1 점수**: 0.75 이상이면 양호
- **AUC**: 0.85 이상이면 우수한 성능

## 🔥 현실성 향상 모듈

### 기본 설정

```python
from realistic_fire_model import RealisticFireModel, DetailedWeatherConditions

# 모델 초기화
fire_model = RealisticFireModel(grid_size=(100, 100), cell_size=30.0)

# 연료 맵 설정
fire_model.fuel_map = your_fuel_map

# 기상 조건 설정
weather = DetailedWeatherConditions(
    temperature=35.0,        # 온도 (°C)
    relative_humidity=25.0,  # 상대습도 (%)
    wind_speed=15.0,         # 풍속 (m/s)
    wind_direction=270.0,    # 풍향 (도)
    atmospheric_pressure=1013.0,
    solar_radiation=800.0,
    precipitation=0.0,
    drought_index=0.8,       # 가뭄 지수 (0-1)
    fire_weather_index=85.0, # 화재 기상 지수
    stability_class='B'      # 대기 안정도
)
fire_model.weather_conditions = weather
```

### 연료 수분 모델링

```python
# 연료별 기본 수분량 설정
base_moisture = {
    'TL1': 0.12,  # 낮은 목재 12%
    'TL2': 0.15,  # 중간 목재 15%
    'GS1': 0.08,  # 짧은 풀 8%
    'GS2': 0.10,  # 중간 풀 10%
    'TU1': 0.14   # 낮은 관목 14%
}

# 계절별 수분 변화 (여름: 0.8, 겨울: 1.2)
seasonal_factor = 0.8  

# 수분 모델 적용
fire_model.set_fuel_moisture_model(
    base_moisture=base_moisture,
    daily_variation=0.05,    # 일일 변동성 5%
    seasonal_factor=seasonal_factor
)
```

### 비화 현상 시뮬레이션

```python
# 현재 화재 상태
current_grid = your_fire_grid

# 비화 시뮬레이션 (최대 1km 거리)
new_ignitions = fire_model.simulate_spotting(
    current_grid, 
    max_spot_distance=1000.0
)

print(f"새로운 착화점: {len(new_ignitions)}개")

# 비화 이벤트 분석
for event in fire_model.spotting_events:
    print(f"출발: {event['source']}, 착지: {event['landing']}")
    print(f"거리: {event['distance']:.1f}m, 풍속: {event['wind_speed']:.1f}m/s")
```

### 진압 활동 시뮬레이션

```python
# 진압 자원 정의
suppression_resources = {
    'ground_crews': [
        {
            'location': (50, 50),    # 위치
            'effectiveness': 0.8,    # 효과성 (0-1)
            'range': 3              # 작업 반경
        }
    ],
    'aerial_drops': [
        {
            'center': (45, 45),      # 살수 중심
            'radius': 8,             # 살수 반경
            'effectiveness': 0.9     # 진압 효과성
        }
    ],
    'firebreaks': [
        {
            'start': (30, 20),       # 방화선 시작점
            'end': (70, 60),         # 방화선 끝점
            'width': 2               # 방화선 폭
        }
    ]
}

# 진압 활동 적용
new_grid = fire_model.simulate_suppression_activities(
    current_grid, 
    suppression_resources
)
```

## 🎯 통합 시스템 사용법

### 완전한 시뮬레이션 실행

```python
from integrated_validation_system import IntegratedValidationSystem

# 1. 시스템 초기화
system = IntegratedValidationSystem()

# 또는 사용자 정의 설정 파일 사용
system = IntegratedValidationSystem("my_config.json")

# 2. 데이터 준비
fuel_map = np.load("fuel_map.npy")
elevation_map = np.load("elevation.npy")

weather_data = {
    'temperature': 32.0,
    'relative_humidity': 30.0,
    'wind_speed': 12.0,
    'wind_direction': 225.0,
    # ... 기타 기상 데이터
}

# 3. 모델 설정
system.setup_models(
    fuel_map=fuel_map,
    elevation_map=elevation_map,
    weather_data=weather_data
)

# 4. 시뮬레이션 실행
ignition_points = [(40, 40), (42, 42)]
results = system.run_integrated_simulation(ignition_points)

# 5. 종합 검증
validation_results = system.run_comprehensive_validation()

# 6. 보고서 생성
report_path = system.generate_comprehensive_report()
print(f"보고서 저장: {report_path}")
```

### 설정 파일 사용

```json
{
  "simulation": {
    "grid_size": [150, 150],
    "cell_size": 30.0,
    "max_steps": 200,
    "validation_interval": 20
  },
  "validation": {
    "enable_pattern_validation": true,
    "enable_temporal_validation": true,
    "enable_confusion_matrix": true,
    "enable_roc_analysis": true
  },
  "realism": {
    "enable_spotting": true,
    "enable_human_influence": true,
    "enable_suppression": true,
    "max_spot_distance": 1500.0
  },
  "output": {
    "save_intermediate_results": true,
    "generate_animations": true,
    "output_directory": "my_simulation_results"
  }
}
```

### 실시간 모니터링

시뮬레이션 중에 성능 지표가 실시간으로 모니터링되며, 자동으로 개선 제안이 생성됩니다:

```python
# 시뮬레이션 진행 중 자동 생성되는 개선 제안 예시
improvement_suggestions = [
    {
        'category': 'validation',
        'priority': 'high',
        'suggestion': 'CA 규칙 파라미터 조정 필요',
        'details': '확산 확률을 0.3에서 0.25로 감소 권장'
    },
    {
        'category': 'realism', 
        'priority': 'medium',
        'suggestion': '비화 현상이 관찰되지 않음',
        'details': '풍속이나 화재 강도 조건을 확인하세요'
    }
]
```

## 📊 결과 해석 가이드

### 1. 검증 점수 해석

#### 종합 점수 등급
- **0.8 이상**: 우수 - 모델이 매우 정확함
- **0.6-0.8**: 양호 - 실용적 수준의 정확도
- **0.4-0.6**: 보통 - 개선 필요
- **0.4 미만**: 부족 - 파라미터 재조정 필요

#### 주요 지표별 기준값
```python
# 예시 결과 해석
validation_results = {
    'confusion_matrix': {
        'accuracy': 0.82,      # 82% 정확도 (양호)
        'f1_score': 0.76,      # F1 점수 (양호)
        'precision': 0.78,     # 정밀도
        'recall': 0.74         # 재현율
    },
    'spread_pattern': {
        'compactness': 0.65,   # 적절한 집중도
        'circularity': 0.58,   # 약간 비원형 (자연스러움)
        'jaccard_similarity': 0.71  # 실제와 71% 유사 (양호)
    }
}
```

### 2. 현실성 지표 해석

```python
realism_metrics = {
    'spotting_events': 15,           # 15회 비화 (적절)
    'max_fire_intensity': 3500.0,    # 최대 강도 3.5MW/m (수관화재 수준)
    'mean_flame_length': 2.3,        # 평균 화염 길이 2.3m (표면화재)
    'fire_behavior_diversity': 3,    # 3가지 화재 행동 (다양성 양호)
    'behavior_distribution': {
        'surface': 150,              # 표면화재가 주도적
        'crown': 25,                 # 일부 수관화재
        'spotting': 15               # 비화 발생
    }
}
```

### 3. 성능 추세 분석

시뮬레이션 진행에 따른 성능 변화를 모니터링:

- **상승 추세**: 모델이 점진적으로 개선됨
- **안정적**: 일관된 성능 (바람직)
- **하락 추세**: 파라미터 재검토 필요
- **불안정**: 설정 오류 가능성

## 🔧 문제 해결

### 자주 발생하는 문제들

#### 1. 메모리 부족 오류
```python
# 해결책: 격자 크기 축소 또는 배치 처리
system.config['simulation']['grid_size'] = [80, 80]  # 기본 100x100에서 축소
```

#### 2. 비화 현상이 발생하지 않음
```python
# 해결책: 기상 조건 강화
weather_data['wind_speed'] = 20.0  # 풍속 증가
weather_data['relative_humidity'] = 15.0  # 습도 감소
```

#### 3. 검증 점수가 낮음
```python
# 해결책: CA 모델 파라미터 조정
ca_model.base_spread_prob = 0.25  # 확산 확률 조정
ca_model.neighbor_influence = 0.8  # 이웃 영향 조정
```

#### 4. 시뮬레이션이 너무 빠르게 진행됨
```python
# 해결책: 연료 수분량 증가
base_moisture = {fuel: val * 1.2 for fuel, val in base_moisture.items()}
```

### 성능 최적화

#### 1. GPU 가속 활용
```python
# PyTorch GPU 사용 (CUDA 설치 필요)
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"사용 중인 디바이스: {device}")
```

#### 2. 병렬 처리 설정
```python
# 설정 파일에서 병렬 처리 활성화
{
  "performance": {
    "use_multiprocessing": true,
    "num_processes": 4,
    "chunk_size": 1000
  }
}
```

#### 3. 메모리 효율화
```python
# 중간 결과 저장 비활성화 (메모리 절약)
system.config['output']['save_intermediate_results'] = False
```

### 로그 및 디버깅

```python
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simulation.log'),
        logging.StreamHandler()
    ]
)

# 디버그 모드 활성화
system.config['debug'] = True
```

## 📚 추가 자료

### 관련 파일들
- `model_validation.py`: 모델 검증 시스템
- `realistic_fire_model.py`: 현실성 향상 모듈  
- `integrated_validation_system.py`: 통합 시스템
- `requirements.txt`: 의존성 목록
- `config_template.json`: 설정 파일 템플릿

### 참고 문헌
1. Anderson, H.E. (1982). Aids to determining fuel models for estimating fire behavior
2. Rothermel, R.C. (1972). A mathematical model for predicting fire spread
3. Finney, M.A. (1998). FARSITE: Fire Area Simulator-model development and evaluation

### 기술 지원
- GitHub Issues: 버그 리포트 및 기능 요청
- 문서: 상세한 API 문서 및 튜토리얼
- 예제: 다양한 사용 사례별 예제 코드

---

**마지막 업데이트**: 2024년 12월 (모델 검증 및 현실성 향상 버전)

이 가이드는 지속적으로 업데이트되며, 사용자 피드백을 반영하여 개선됩니다.
