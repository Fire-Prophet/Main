"""
PostgreSQL 화재 시뮬레이션 모듈
토양 데이터와 임상도 데이터를 PostgreSQL에서 가져와 화재 시뮬레이션을 수행하는 모듈
"""

try:
    from .spatial_data_extractor import SpatialDataExtractor
    from .fire_simulation_connector import FireSimulationConnector
    from .forest_data_processor import ForestDataProcessor
    from .soil_data_processor import SoilDataProcessor
    from .fire_model_integrator import FireModelIntegrator
except ImportError:
    # 패키지 외부에서 실행할 때
    from spatial_data_extractor import SpatialDataExtractor
    from fire_simulation_connector import FireSimulationConnector
    from forest_data_processor import ForestDataProcessor
    from soil_data_processor import SoilDataProcessor
    from fire_model_integrator import FireModelIntegrator

__version__ = "1.0.0"
__author__ = "Fire Simulation Team"

__all__ = [
    'SpatialDataExtractor',
    'FireSimulationConnector', 
    'ForestDataProcessor',
    'SoilDataProcessor',
    'FireModelIntegrator'
]
