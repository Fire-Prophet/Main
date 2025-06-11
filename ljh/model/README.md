# 화재 시뮬레이션 모델 (Fire Simulation Model)

## 프로젝트 개요
이 프로젝트는 Cellular Automata (CA) 기반의 화재 확산 시뮬레이션 모델입니다. 실제 지형, 기상 조건, 연료 타입을 고려하여 화재의 확산 패턴을 예측하고 시각화합니다.

## 주요 기능
- **화재 확산 시뮬레이션**: CA 기반 알고리즘으로 화재 확산 모델링
- **실시간 기상 데이터 연동**: 온도, 습도, 풍속 등 기상 조건 반영
- **지형 데이터 처리**: DEM, 경사도, 연료 맵 등 지형 정보 활용
- **검증 및 현실성 평가**: 모델 성능 검증 및 현실성 지표 제공
- **시각화**: 화재 진행 과정의 애니메이션 및 통계 차트 생성

## 설치 및 실행

### 요구사항
```bash
pip install -r requirements.txt
```

### 기본 실행
```bash
python main.py
```

### 통합 시뮬레이션 실행
```bash
python integrated_fire_simulation.py
```

## 프로젝트 구조
```
model/
├── main.py                           # 메인 실행 파일
├── integrated_fire_simulation.py     # 통합 시뮬레이션 시스템
├── ca_base.py                        # CA 기본 모델
├── advanced_ca_model.py              # 고급 CA 모델
├── realistic_fire_model.py           # 현실적 화재 모델
├── integrated_validation_system.py   # 검증 시스템
├── terrain_model.py                  # 지형 모델
├── weather_integration.py            # 기상 데이터 연동
├── grid.py                           # 격자 시스템
├── shapefile.py                      # Shapefile 처리
├── label.py                          # 라벨링 데이터
├── ca_analyzer.py                    # CA 분석기
└── requirements.txt                  # 의존성 목록
```

## 데이터 수집 및 전처리
1. **지형·연료·토양 데이터 불러오기**
   - GeoTIFF나 Shapefile 형태의 지형고도·연료맵을 Rasterio/GeoPandas로 로드
2. **실시간 기상 API 연동**
   - MetPy 또는 Siphon 등으로 온도·습도·풍속 데이터 수집 스크립트 작성
3. **데이터 정합성 체크**
   - 좌표계 통일 (PyProj), 결측치 처리, 해상도 리샘플링
4. **EDA(탐색적 분석)**
   - Matplotlib/Seaborn으로 주요 변수 분포와 상관관계 시각화

## 사용 예제
```python
from integrated_fire_simulation import IntegratedFireSimulation

# 시뮬레이션 설정
config = {
    'grid_size': (100, 100),
    'simulation_steps': 50,
    'weather_conditions': {
        'wind_speed': 10,
        'wind_direction': 45,
        'temperature': 25,
        'humidity': 30
    }
}

# 시뮬레이션 실행
sim = IntegratedFireSimulation(config)
results = sim.run_simulation()
sim.generate_report()
```

## 결과 해석
- **시뮬레이션 요약**: `simulation_summary.md`에서 전체 결과 확인
- **시각화 결과**: `demo_scenario_results/` 폴더의 PNG, GIF 파일들
- **상세 보고서**: `comprehensive_report.json`에서 수치 데이터 확인

## 기여하기
1. Fork 프로젝트
2. Feature 브랜치 생성 (`git checkout -b feature/새기능`)
3. 변경사항 커밋 (`git commit -am '새기능 추가'`)
4. 브랜치에 Push (`git push origin feature/새기능`)
5. Pull Request 생성

## 라이선스
MIT License
