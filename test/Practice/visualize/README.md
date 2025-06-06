# Fire Simulation Map Visualization System

Python 기반의 화재 시뮬레이션 결과를 지도 위에 시각화하는 종합 시스템입니다.

## 기능

- **인터랙티브 지도 시각화**: Folium을 사용한 웹 기반 지도
- **시간 경과 애니메이션**: 화재 확산 과정의 시간별 애니메이션
- **다양한 차트**: Plotly를 활용한 인터랙티브 차트와 3D 시각화
- **웹 대시보드**: Streamlit 기반의 완전한 웹 인터페이스
- **모듈러 아키텍처**: 8개의 전문화된 Python 모듈
- **데이터 내보내기**: JSON, GeoJSON, CSV 형식 지원

## 설치

### 1. 요구사항

```bash
pip install -r requirements.txt
```

### 2. 패키지 설치

```bash
# 개발 모드로 설치
pip install -e .

# 또는 직접 설치
python setup.py install
```

## 사용 방법

### 1. 기본 사용법

```python
from visualize import FireMapVisualizer

# 시각화 시스템 초기화
visualizer = FireMapVisualizer()

# 시뮬레이션 데이터 로드
visualizer.load_simulation_data('path/to/simulation_data.json')

# 기본 지도 생성
map_obj = visualizer.create_basic_map()
map_obj.save('fire_map.html')
```

### 2. 웹 인터페이스 실행

```python
# 웹 대시보드 실행
visualizer.launch_web_interface()
```

또는 명령줄에서:

```bash
python -m visualize.fire_map_visualizer --data simulation_data.json --web
```

### 3. 애니메이션 생성

```python
# 화재 확산 애니메이션 생성
animation_path = visualizer.create_animation()
```

### 4. 종합 보고서 생성

```python
# 지도, 차트, 통계를 포함한 HTML 보고서
report_path = visualizer.create_comprehensive_report()
```

### 5. 차트 생성

```python
# 모든 차트 생성
chart_paths = visualizer.generate_comprehensive_charts()

# 개별 차트 생성
chart_gen = visualizer.chart_generator
evolution_fig = chart_gen.create_time_evolution_chart()
heatmap_fig = chart_gen.create_fire_intensity_heatmap()
```

## 명령줄 사용법

```bash
# 기본 지도 생성
python -m visualize.fire_map_visualizer --data simulation_data.json

# 웹 인터페이스 실행
python -m visualize.fire_map_visualizer --data simulation_data.json --web

# 종합 보고서 생성
python -m visualize.fire_map_visualizer --data simulation_data.json --report

# 애니메이션 생성
python -m visualize.fire_map_visualizer --data simulation_data.json --animation

# 출력 디렉토리 지정
python -m visualize.fire_map_visualizer --data simulation_data.json --output results/
```

## 설정

`config.json` 파일을 통해 시각화 설정을 커스터마이징할 수 있습니다:

```json
{
  "map": {
    "default_center": [37.5665, 126.9780],
    "default_zoom": 10,
    "tile_layer": "OpenStreetMap"
  },
  "colors": {
    "fire_states": {
      "empty": "#FFFFFF",
      "fuel": "#228B22",
      "burning": "#FF4500",
      "burned": "#8B4513"
    }
  },
  "animation": {
    "interval": 1000,
    "auto_play": false
  }
}
```

## 데이터 형식

시뮬레이션 JSON 데이터는 다음 형식을 따라야 합니다:

```json
{
  "metadata": {
    "simulation_id": "sim_001",
    "timestamp": "2024-01-15T10:30:00",
    "parameters": {...}
  },
  "geographic_bounds": {
    "min_lat": 36.0,
    "max_lat": 37.0,
    "min_lon": 126.0,
    "max_lon": 127.0
  },
  "steps": [
    {
      "step": 0,
      "grid": [[1, 1, 0], [1, 2, 2], [0, 3, 3]],
      "grid_shape": [3, 3],
      "stats": {
        "burning_cells": 2,
        "burned_cells": 2,
        "burn_ratio": 0.67
      }
    }
  ]
}
```

### 격자 상태 코드
- `0`: 빈 공간
- `1`: 연료 (아직 타지 않음)
- `2`: 현재 연소 중
- `3`: 이미 탄 지역

## 모듈 구조

```
visualize/
├── __init__.py                  # 패키지 초기화
├── config.py                    # 설정 관리
├── data_loader.py              # 데이터 로더
├── layer_manager.py            # 레이어 관리
├── map_renderer.py             # 지도 렌더링
├── animation_controller.py     # 애니메이션 제어
├── chart_generator.py          # 차트 생성
├── web_interface.py           # 웹 인터페이스
└── fire_map_visualizer.py     # 메인 오케스트레이터
```

## 예제

### 예제 1: 기본 시각화

```python
from visualize import FireMapVisualizer

visualizer = FireMapVisualizer()
visualizer.load_simulation_data('examples/sample_simulation.json')

# 최종 상태 지도
final_map = visualizer.create_basic_map(step=-1)
final_map.save('final_fire_state.html')

# 통계 확인
stats = visualizer.get_simulation_statistics()
print(f"총 스텝: {stats['total_steps']}")
print(f"최대 연소 셀: {stats['max_burning_cells']}")
```

### 예제 2: 커스텀 설정

```python
# 커스텀 설정으로 초기화
visualizer = FireMapVisualizer('custom_config.json')

# 인터랙티브 지도 (타임라인 포함)
interactive_map = visualizer.create_interactive_map()
interactive_map.save('interactive_fire_map.html')
```

### 예제 3: 데이터 내보내기

```python
# GeoJSON으로 내보내기
geojson_path = visualizer.export_data('geojson')

# CSV로 내보내기
csv_path = visualizer.export_data('csv')
```

## 웹 인터페이스 기능

웹 대시보드는 다음 기능을 제공합니다:

- **파일 업로드**: 시뮬레이션 데이터 파일 업로드
- **실시간 지도**: 인터랙티브 지도 표시
- **애니메이션 제어**: 재생/일시정지/스텝별 이동
- **차트 뷰어**: 다양한 분석 차트
- **설정 패널**: 색상, 투명도 등 시각화 설정
- **내보내기**: 지도, 차트, 데이터 내보내기

## 개발자 정보

이 시스템은 PostGIS 공간 데이터베이스와 연동되는 화재 시뮬레이션 모델의 결과를 시각화하기 위해 개발되었습니다.

## 라이선스

MIT License

## 기여

버그 리포트나 기능 제안은 GitHub Issues를 통해 제출해 주세요.
