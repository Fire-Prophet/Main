"""
화재 시뮬레이션 지도 시각화 시스템

주요 컴포넌트:
- FireMapVisualizer: 메인 시각화 클래스
- 각종 전문화된 모듈들
"""

__version__ = "1.0.0"
__author__ = "Fire Simulation Team"

# Import all main classes to make them available at package level
try:
    from .data_loader import SimulationDataLoader as FireSimulationDataLoader
    from .map_renderer import MapRenderer
    from .layer_manager import LayerManager
    from .animation_controller import AnimationController
    from .chart_generator import ChartGenerator
    from .config import UI_CONFIG
    from .fire_map_visualizer import FireMapVisualizer
except ImportError:
    # Create dummy classes for fallback
    class FireSimulationDataLoader:
        def __init__(self, *args, **kwargs):
            pass
    
    class MapRenderer:
        def __init__(self, *args, **kwargs):
            pass
    
    class LayerManager:
        def __init__(self, *args, **kwargs):
            pass
    
    class AnimationController:
        def __init__(self, *args, **kwargs):
            pass
    
    class ChartGenerator:
        def __init__(self, *args, **kwargs):
            pass
    
    class FireMapVisualizer:
        def __init__(self, *args, **kwargs):
            pass
    
    UI_CONFIG = {
        'title': 'Fire Simulation Visualizer',
        'sidebar_width': 300
    }

__all__ = [
    'FireSimulationDataLoader',
    'MapRenderer', 
    'LayerManager',
    'AnimationController',
    'ChartGenerator',
    'FireMapVisualizer',
    'UI_CONFIG'
]

# 메인 클래스 import
from .fire_map_visualizer import FireMapVisualizer

# 개별 컴포넌트 import
from .config import VisualizationConfig
from .data_loader import SimulationDataLoader
from .layer_manager import LayerManager
from .map_renderer import MapRenderer
from .animation_controller import AnimationController
from .chart_generator import ChartGenerator
from .web_interface import WebInterface

# 편의 함수들
__all__ = [
    'FireMapVisualizer',
    'VisualizationConfig',
    'SimulationDataLoader',
    'LayerManager',
    'MapRenderer', 
    'AnimationController',
    'ChartGenerator',
    'WebInterface'
]

def create_visualizer(config_path=None):
    """
    편의 함수: FireMapVisualizer 인스턴스 생성
    
    Args:
        config_path: 설정 파일 경로 (선택사항)
        
    Returns:
        FireMapVisualizer: 초기화된 시각화 객체
    """
    return FireMapVisualizer(config_path)

def quick_visualize(data_path, output_path=None):
    """
    편의 함수: 빠른 시각화 생성
    
    Args:
        data_path: 시뮬레이션 데이터 파일 경로
        output_path: 출력 파일 경로 (선택사항)
        
    Returns:
        str: 생성된 지도 파일 경로
    """
    visualizer = FireMapVisualizer()
    
    if not visualizer.load_simulation_data(data_path):
        raise ValueError(f"데이터 로드 실패: {data_path}")
    
    map_obj = visualizer.create_basic_map()
    
    if not output_path:
        output_path = "fire_visualization.html"
    
    map_obj.save(output_path)
    return output_path
