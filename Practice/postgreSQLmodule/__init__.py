"""
PostgreSQL 모듈 패키지
데이터베이스 연결, 데이터 처리, 분석을 위한 통합 모듈
"""

from .database import PostgreSQLManager
from .data_processor import DataProcessor
from .analyzer import DataAnalyzer
from .exporter import DataExporter
from .integration import PostgreSQLIntegrator
from .config import Config

__version__ = "1.0.0"
__author__ = "PostgreSQL Module Team"

__all__ = [
    'PostgreSQLManager',
    'DataProcessor', 
    'DataAnalyzer',
    'DataExporter',
    'PostgreSQLIntegrator',
    'Config'
]

# 기본 로깅 설정
Config.setup_logging()
