#!/usr/bin/env python3
"""
화재 시뮬레이션 Streamlit 웹 인터페이스
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from pathlib import Path
import sys
from io import BytesIO
import zipfile

# 프로젝트 모듈 import
sys.path.append(str(Path(__file__).parent))

try:
    from integrated_validation_system import IntegratedValidationSystem
    from model_validation import ModelValidator
    from realistic_fire_model import RealisticFireModel
    from ca_base import CellularAutomaton
    from performance_monitor import global_monitor, start_monitoring, stop_monitoring
except ImportError as e:
    st.error(f"모듈 import 오류: {e}")
    st.stop()


def setup_page():
    """페이지 설정"""
    st.set_page_config(
        page_title="🔥 화재 시뮬레이션 대시보드",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔥 한국 산림 화재 확산 시뮬레이션")
    st.markdown("---")


def sidebar_configuration():
    """사이드바 설정"""
    st.sidebar.header("🎛️ 시뮬레이션 설정")
    
    # 격자 설정
    st.sidebar.subheader("격자 설정")
    grid_width = st.sidebar.slider("격자 너비", 50, 200, 100)
    grid_height = st.sidebar.slider("격자 높이", 50, 200, 100)
    cell_size = st.sidebar.number_input("셀 크기 (m)", 10.0, 100.0, 30.0)
    
    # 시뮬레이션 설정
    st.sidebar.subheader("시뮬레이션 설정")
    max_steps = st.sidebar.slider("최대 스텝 수", 10, 500, 100)
    ignition_count = st.sidebar.slider("점화점 수", 1, 10, 1)
    
    # 기상 조건
    st.sidebar.subheader("기상 조건")
    temperature = st.sidebar.slider("온도 (°C)", 0, 50, 25)
    humidity = st.sidebar.slider("상대습도 (%)", 10, 90, 50)
    wind_speed = st.sidebar.slider("풍속 (m/s)", 0, 30, 10)
    wind_direction = st.sidebar.slider("풍향 (도)", 0, 360, 270)
    
    # 현실성 옵션
    st.sidebar.subheader("현실성 옵션")
    enable_spotting = st.sidebar.checkbox("비화 현상", True)
    enable_suppression = st.sidebar.checkbox("진압 활동", False)
    enable_human_factors = st.sidebar.checkbox("인간 요인", True)
    
    return {
        'grid_size': (grid_width, grid_height),
        'cell_size': cell_size,
        'max_steps': max_steps,
        'ignition_count': ignition_count,
        'weather': {
            'temperature': temperature,
            'relative_humidity': humidity,
            'wind_speed': wind_speed,
            'wind_direction': wind_direction
        },
        'realism': {
            'enable_spotting': enable_spotting,
            'enable_suppression': enable_suppression,
            'enable_human_factors': enable_human_factors
        }
    }


def create_sample_fuel_map(grid_size):
    """샘플 연료 맵 생성"""
    width, height = grid_size
    fuel_map = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], 
                               size=(height, width),
                               p=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.03, 0.01, 0.01])
    return fuel_map


def visualize_fuel_map(fuel_map):
    """연료 맵 시각화"""
    fig = px.imshow(fuel_map, 
                   title="연료 분포도",
                   labels={'x': 'X 좌표', 'y': 'Y 좌표', 'color': '연료 타입'},
                   color_continuous_scale='Viridis')
    return fig


def visualize_fire_progression(results):
    """화재 진행 과정 시각화"""
    if not results or 'grids' not in results:
        return None
    
    grids = results['grids']
    steps_to_show = min(10, len(grids))
    step_indices = np.linspace(0, len(grids)-1, steps_to_show, dtype=int)
    
    fig = make_subplots(
        rows=2, cols=5,
        subplot_titles=[f"Step {i}" for i in step_indices],
        specs=[[{'type': 'heatmap'} for _ in range(5)] for _ in range(2)]
    )
    
    for idx, step_idx in enumerate(step_indices):
        row = idx // 5 + 1
        col = idx % 5 + 1
        
        fig.add_trace(
            go.Heatmap(z=grids[step_idx], showscale=False, colorscale='Hot'),
            row=row, col=col
        )
    
    fig.update_layout(
        title="화재 확산 과정",
        height=600,
        showlegend=False
    )
    
    return fig


def create_metrics_chart(validation_results):
    """검증 메트릭 차트 생성"""
    if not validation_results:
        return None
    
    # 메트릭 데이터 준비
    metrics_data = []
    
    if 'confusion_matrix' in validation_results:
        cm = validation_results['confusion_matrix']
        for metric, value in cm.items():
            metrics_data.append({'Metric': metric.title(), 'Value': value, 'Category': 'Classification'})
    
    if 'spread_pattern' in validation_results:
        sp = validation_results['spread_pattern']
        for metric, value in sp.items():
            metrics_data.append({'Metric': metric.title(), 'Value': value, 'Category': 'Pattern'})
    
    if not metrics_data:
        return None
    
    df = pd.DataFrame(metrics_data)
    
    fig = px.bar(df, x='Metric', y='Value', color='Category',
                title="모델 검증 메트릭",
                labels={'Value': '점수', 'Metric': '메트릭'})
    
    # 기준선 추가
    fig.add_hline(y=0.8, line_dash="dash", line_color="green", 
                 annotation_text="우수 (0.8)")
    fig.add_hline(y=0.6, line_dash="dash", line_color="orange", 
                 annotation_text="양호 (0.6)")
    
    return fig


def display_performance_metrics():
    """성능 메트릭 표시"""
    st.subheader("🚀 성능 메트릭")
    
    if not global_monitor.metrics_history:
        st.info("아직 성능 데이터가 없습니다. 시뮬레이션을 실행해보세요.")
        return
    
    # 최근 성능 통계
    recent_metrics = global_monitor.metrics_history[-10:]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_duration = np.mean([m.duration for m in recent_metrics])
        st.metric("평균 실행 시간", f"{avg_duration:.2f}초")
    
    with col2:
        avg_memory = np.mean([m.memory_used for m in recent_metrics])
        st.metric("평균 메모리 사용", f"{avg_memory:.1f}MB")
    
    with col3:
        avg_cpu = np.mean([m.cpu_percent for m in recent_metrics])
        st.metric("평균 CPU 사용률", f"{avg_cpu:.1f}%")
    
    with col4:
        total_runs = len(global_monitor.metrics_history)
        st.metric("총 실행 횟수", total_runs)
    
    # 성능 트렌드 차트
    if len(recent_metrics) > 1:
        chart_data = pd.DataFrame({
            'Step': range(len(recent_metrics)),
            'Duration': [m.duration for m in recent_metrics],
            'Memory': [m.memory_used for m in recent_metrics]
        })
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=chart_data['Step'], y=chart_data['Duration'], 
                      name="실행 시간 (초)", line=dict(color='blue')),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=chart_data['Step'], y=chart_data['Memory'], 
                      name="메모리 사용 (MB)", line=dict(color='red')),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="실행 순서")
        fig.update_yaxes(title_text="실행 시간 (초)", secondary_y=False)
        fig.update_yaxes(title_text="메모리 사용 (MB)", secondary_y=True)
        
        fig.update_layout(title="성능 트렌드", height=400)
        
        st.plotly_chart(fig, use_container_width=True)


def run_simulation(config):
    """시뮬레이션 실행"""
    try:
        # 시스템 초기화
        system = IntegratedValidationSystem()
        
        # 샘플 데이터 생성
        fuel_map = create_sample_fuel_map(config['grid_size'])
        elevation_map = np.random.random(config['grid_size']) * 100  # 0-100m 고도
        
        # 모델 설정
        system.setup_models(
            fuel_map=fuel_map,
            elevation_map=elevation_map,
            weather_data=config['weather']
        )
        
        # 점화점 생성
        width, height = config['grid_size']
        ignition_points = []
        for _ in range(config['ignition_count']):
            x = np.random.randint(width // 4, 3 * width // 4)
            y = np.random.randint(height // 4, 3 * height // 4)
            ignition_points.append((x, y))
        
        # 성능 모니터링과 함께 시뮬레이션 실행
        with global_monitor.monitor("full_simulation"):
            results = system.run_integrated_simulation(
                ignition_points=ignition_points,
                max_steps=config['max_steps'],
                enable_spotting=config['realism']['enable_spotting'],
                enable_suppression=config['realism']['enable_suppression']
            )
        
        # 검증 실행
        with global_monitor.monitor("validation"):
            validation_results = system.run_comprehensive_validation()
        
        return {
            'results': results,
            'validation': validation_results,
            'fuel_map': fuel_map,
            'ignition_points': ignition_points
        }
        
    except Exception as e:
        st.error(f"시뮬레이션 실행 중 오류 발생: {e}")
        return None


def download_results(results):
    """결과 다운로드"""
    if not results:
        return
    
    # 결과를 JSON으로 직렬화 (numpy 배열 처리)
    downloadable_results = {}
    
    for key, value in results.items():
        if isinstance(value, np.ndarray):
            downloadable_results[key] = value.tolist()
        elif isinstance(value, dict):
            downloadable_results[key] = {}
            for k, v in value.items():
                if isinstance(v, np.ndarray):
                    downloadable_results[key][k] = v.tolist()
                else:
                    downloadable_results[key][k] = v
        else:
            downloadable_results[key] = value
    
    # JSON 파일 생성
    json_str = json.dumps(downloadable_results, indent=2, ensure_ascii=False)
    json_bytes = json_str.encode('utf-8')
    
    st.download_button(
        label="📥 결과 다운로드 (JSON)",
        data=json_bytes,
        file_name=f"fire_simulation_results_{int(time.time())}.json",
        mime="application/json"
    )


def main():
    """메인 함수"""
    setup_page()
    
    # 백그라운드 모니터링 시작
    if 'monitoring_started' not in st.session_state:
        start_monitoring()
        st.session_state.monitoring_started = True
    
    # 설정 사이드바
    config = sidebar_configuration()
    
    # 메인 컨텐츠 영역
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 시뮬레이션", "📊 결과 분석", "🚀 성능", "📚 도움말"])
    
    with tab1:
        st.header("시뮬레이션 실행")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 연료 맵 미리보기
            st.subheader("연료 분포 미리보기")
            fuel_map = create_sample_fuel_map(config['grid_size'])
            fuel_fig = visualize_fuel_map(fuel_map)
            st.plotly_chart(fuel_fig, use_container_width=True)
        
        with col2:
            st.subheader("시뮬레이션 제어")
            
            if st.button("🚀 시뮬레이션 시작", type="primary"):
                with st.spinner("시뮬레이션 실행 중..."):
                    start_time = time.time()
                    
                    # 진행률 표시
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i in range(10):
                        progress_bar.progress((i + 1) / 10)
                        status_text.text(f"진행률: {(i+1)*10}%")
                        time.sleep(0.1)
                    
                    # 실제 시뮬레이션 실행
                    results = run_simulation(config)
                    
                    end_time = time.time()
                    
                    if results:
                        st.session_state.simulation_results = results
                        st.success(f"시뮬레이션 완료! (소요시간: {end_time-start_time:.2f}초)")
                    else:
                        st.error("시뮬레이션 실행 실패")
            
            if st.button("🔄 결과 초기화"):
                if 'simulation_results' in st.session_state:
                    del st.session_state.simulation_results
                global_monitor.clear_history()
                st.success("결과가 초기화되었습니다.")
    
    with tab2:
        st.header("결과 분석")
        
        if 'simulation_results' in st.session_state:
            results = st.session_state.simulation_results
            
            # 화재 진행 과정
            if results['results']:
                fire_fig = visualize_fire_progression(results['results'])
                if fire_fig:
                    st.plotly_chart(fire_fig, use_container_width=True)
            
            # 검증 메트릭
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("검증 메트릭")
                if results['validation']:
                    metrics_fig = create_metrics_chart(results['validation'])
                    if metrics_fig:
                        st.plotly_chart(metrics_fig, use_container_width=True)
            
            with col2:
                st.subheader("시뮬레이션 정보")
                if results['results']:
                    info_data = {
                        "총 스텝 수": len(results['results'].get('grids', [])),
                        "점화점 수": len(results.get('ignition_points', [])),
                        "격자 크기": f"{config['grid_size'][0]} × {config['grid_size'][1]}",
                        "셀 크기": f"{config['cell_size']}m",
                        "최종 연소 면적": f"{np.sum(results['results']['grids'][-1] > 0) if results['results']['grids'] else 0} 셀"
                    }
                    
                    for key, value in info_data.items():
                        st.metric(key, value)
            
            # 다운로드 버튼
            st.subheader("결과 다운로드")
            download_results(results)
            
        else:
            st.info("먼저 시뮬레이션을 실행해주세요.")
    
    with tab3:
        display_performance_metrics()
    
    with tab4:
        st.header("사용 가이드")
        
        st.markdown("""
        ## 🔥 화재 시뮬레이션 사용법
        
        ### 1. 기본 설정
        - **격자 설정**: 시뮬레이션할 지역의 크기와 해상도를 설정합니다.
        - **시뮬레이션 설정**: 최대 스텝 수와 점화점 개수를 조정합니다.
        
        ### 2. 기상 조건
        - **온도**: 높을수록 화재 확산이 빨라집니다.
        - **습도**: 낮을수록 화재 위험이 증가합니다.
        - **풍속/풍향**: 화재 확산 방향과 속도에 영향을 줍니다.
        
        ### 3. 현실성 옵션
        - **비화 현상**: 바람에 의한 원거리 착화를 시뮬레이션합니다.
        - **진압 활동**: 소방 활동의 효과를 모델링합니다.
        - **인간 요인**: 도로, 전력선 등의 영향을 고려합니다.
        
        ### 4. 결과 해석
        - **검증 메트릭**: 0.8 이상이면 우수, 0.6-0.8이면 양호한 성능입니다.
        - **성능 지표**: 실행 시간과 메모리 사용량을 모니터링합니다.
        
        ### 5. 문제 해결
        - 메모리 부족 시 격자 크기를 줄여보세요.
        - 실행 시간이 길면 최대 스텝 수를 조정하세요.
        """)


if __name__ == '__main__':
    main()
