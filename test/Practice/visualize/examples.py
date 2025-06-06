"""
화재 시뮬레이션 지도 시각화 시스템 예제
"""

import os
import sys
from pathlib import Path

# 패키지 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from visualize import FireMapVisualizer


def create_sample_data():
    """샘플 시뮬레이션 데이터 생성"""
    import json
    import numpy as np
    
    # 간단한 화재 확산 시뮬레이션 생성
    grid_size = 20
    steps = []
    
    # 초기 상태: 중앙에 연료, 한 점에서 화재 시작
    initial_grid = np.ones((grid_size, grid_size))  # 모든 곳에 연료
    initial_grid[10, 10] = 2  # 중앙에서 화재 시작
    
    current_grid = initial_grid.copy()
    
    for step in range(15):  # 15 스텝 시뮬레이션
        # 화재 확산 시뮬레이션 (간단한 버전)
        new_grid = current_grid.copy()
        burning_positions = np.where(current_grid == 2)
        
        for i, j in zip(burning_positions[0], burning_positions[1]):
            # 이미 타고 있는 곳은 탄 상태로
            new_grid[i, j] = 3
            
            # 주변으로 화재 확산
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    ni, nj = i + di, j + dj
                    if (0 <= ni < grid_size and 0 <= nj < grid_size and 
                        current_grid[ni, nj] == 1):  # 연료가 있는 곳만
                        if np.random.random() < 0.3:  # 30% 확률로 확산
                            new_grid[ni, nj] = 2
        
        # 통계 계산
        burning_cells = np.sum(new_grid == 2)
        burned_cells = np.sum(new_grid == 3)
        total_fuel_cells = grid_size * grid_size
        burn_ratio = (burning_cells + burned_cells) / total_fuel_cells
        
        step_data = {
            "step": step,
            "grid": new_grid.tolist(),
            "grid_shape": [grid_size, grid_size],
            "stats": {
                "burning_cells": int(burning_cells),
                "burned_cells": int(burned_cells),
                "burn_ratio": float(burn_ratio)
            }
        }
        steps.append(step_data)
        current_grid = new_grid
    
    # 전체 시뮬레이션 데이터
    simulation_data = {
        "metadata": {
            "simulation_id": "sample_simulation_001",
            "timestamp": "2024-01-15T10:30:00Z",
            "description": "샘플 화재 확산 시뮬레이션",
            "parameters": {
                "grid_size": grid_size,
                "fire_spread_probability": 0.3,
                "wind_speed": 0,
                "wind_direction": 0
            }
        },
        "geographic_bounds": {
            "min_lat": 37.0,
            "max_lat": 37.1,
            "min_lon": 126.0,
            "max_lon": 126.1
        },
        "steps": steps
    }
    
    return simulation_data


def example_basic_visualization():
    """기본 시각화 예제"""
    print("=== 기본 시각화 예제 ===")
    
    # 샘플 데이터 생성
    sample_data = create_sample_data()
    
    # 임시 파일로 저장
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f, indent=2)
        temp_file = f.name
    
    try:
        # 시각화 시스템 초기화
        visualizer = FireMapVisualizer()
        
        # 데이터 로드
        success = visualizer.load_simulation_data(temp_file)
        if not success:
            print("데이터 로드 실패")
            return
        
        # 기본 지도 생성 (최종 상태)
        final_step = len(sample_data['steps']) - 1
        map_obj = visualizer.create_basic_map(final_step)
        
        # 저장
        output_path = "example_basic_map.html"
        map_obj.save(output_path)
        print(f"기본 지도 저장 완료: {output_path}")
        
        # 통계 출력
        stats = visualizer.get_simulation_statistics()
        print(f"총 스텝 수: {stats['total_steps']}")
        print(f"최대 연소 셀: {stats['max_burning_cells']}")
        print(f"최종 연소 비율: {stats['final_burn_ratio']:.2%}")
        
    finally:
        # 임시 파일 삭제
        os.unlink(temp_file)


def example_animation():
    """애니메이션 생성 예제"""
    print("\n=== 애니메이션 생성 예제 ===")
    
    # 샘플 데이터 생성
    sample_data = create_sample_data()
    
    # 임시 파일로 저장
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f, indent=2)
        temp_file = f.name
    
    try:
        # 시각화 시스템 초기화
        visualizer = FireMapVisualizer()
        visualizer.load_simulation_data(temp_file)
        
        # 애니메이션 생성
        animation_path = visualizer.create_animation("example_animation.html")
        print(f"애니메이션 생성 완료: {animation_path}")
        
    finally:
        os.unlink(temp_file)


def example_charts():
    """차트 생성 예제"""
    print("\n=== 차트 생성 예제 ===")
    
    # 샘플 데이터 생성
    sample_data = create_sample_data()
    
    # 임시 파일로 저장
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f, indent=2)
        temp_file = f.name
    
    try:
        # 시각화 시스템 초기화
        visualizer = FireMapVisualizer()
        visualizer.load_simulation_data(temp_file)
        
        # 차트 생성
        output_dir = "example_charts"
        chart_paths = visualizer.generate_comprehensive_charts(output_dir)
        
        print("생성된 차트:")
        for chart_name, path in chart_paths.items():
            print(f"  - {chart_name}: {path}")
        
    finally:
        os.unlink(temp_file)


def example_interactive_map():
    """인터랙티브 지도 예제"""
    print("\n=== 인터랙티브 지도 예제 ===")
    
    # 샘플 데이터 생성
    sample_data = create_sample_data()
    
    # 임시 파일로 저장
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f, indent=2)
        temp_file = f.name
    
    try:
        # 시각화 시스템 초기화
        visualizer = FireMapVisualizer()
        visualizer.load_simulation_data(temp_file)
        
        # 인터랙티브 지도 생성
        interactive_map = visualizer.create_interactive_map()
        
        # 저장
        output_path = "example_interactive_map.html"
        interactive_map.save(output_path)
        print(f"인터랙티브 지도 저장 완료: {output_path}")
        
    finally:
        os.unlink(temp_file)


def example_comprehensive_report():
    """종합 보고서 생성 예제"""
    print("\n=== 종합 보고서 생성 예제 ===")
    
    # 샘플 데이터 생성
    sample_data = create_sample_data()
    
    # 임시 파일로 저장
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f, indent=2)
        temp_file = f.name
    
    try:
        # 시각화 시스템 초기화
        visualizer = FireMapVisualizer()
        visualizer.load_simulation_data(temp_file)
        
        # 종합 보고서 생성
        report_path = visualizer.create_comprehensive_report("example_report.html")
        print(f"종합 보고서 생성 완료: {report_path}")
        
    finally:
        os.unlink(temp_file)


def example_data_export():
    """데이터 내보내기 예제"""
    print("\n=== 데이터 내보내기 예제 ===")
    
    # 샘플 데이터 생성
    sample_data = create_sample_data()
    
    # 임시 파일로 저장
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f, indent=2)
        temp_file = f.name
    
    try:
        # 시각화 시스템 초기화
        visualizer = FireMapVisualizer()
        visualizer.load_simulation_data(temp_file)
        
        # 여러 형식으로 내보내기
        json_path = visualizer.export_data('json', 'exported_data.json')
        print(f"JSON 내보내기 완료: {json_path}")
        
        geojson_path = visualizer.export_data('geojson', 'exported_data.geojson')
        print(f"GeoJSON 내보내기 완료: {geojson_path}")
        
        csv_path = visualizer.export_data('csv', 'exported_data.csv')
        print(f"CSV 내보내기 완료: {csv_path}")
        
    finally:
        os.unlink(temp_file)


def main():
    """모든 예제 실행"""
    print("화재 시뮬레이션 지도 시각화 시스템 예제")
    print("=" * 50)
    
    # 모든 예제 실행
    example_basic_visualization()
    example_animation()
    example_charts()
    example_interactive_map()
    example_comprehensive_report()
    example_data_export()
    
    print("\n모든 예제 실행 완료!")
    print("생성된 파일들을 웹 브라우저로 열어서 결과를 확인하세요.")


if __name__ == "__main__":
    main()
