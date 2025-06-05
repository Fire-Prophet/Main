#!/usr/bin/env python3
"""
PostgreSQL Module Configuration
모듈 설정 및 상수 정의
"""

import os
from typing import Dict, Any


class Config:
    """모듈 설정 클래스"""
    
    # 데이터베이스 기본 설정
    DEFAULT_DB_CONFIG = {
        'host': os.getenv('POSTGRES_HOST', '123.212.210.230'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'database': os.getenv('POSTGRES_DB', 'gis_db'),
        'password': os.getenv('POSTGRES_PASSWORD')
    }
    
    # 내보내기 기본 설정
    DEFAULT_EXPORT_DIR = os.getenv('EXPORT_DIR', 'exports')
    
    # 로깅 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 데이터 처리 기본값
    DEFAULT_CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 10000))
    DEFAULT_ENCODING = os.getenv('DEFAULT_ENCODING', 'utf-8-sig')
    
    # 분석 임계값
    CORRELATION_THRESHOLD = float(os.getenv('CORRELATION_THRESHOLD', 0.5))
    OUTLIER_THRESHOLD = float(os.getenv('OUTLIER_THRESHOLD', 1.5))
    SIGNIFICANCE_LEVEL = float(os.getenv('SIGNIFICANCE_LEVEL', 0.05))
    
    # 성능 설정
    MAX_MEMORY_USAGE_MB = int(os.getenv('MAX_MEMORY_USAGE_MB', 1024))
    MAX_ROWS_FOR_ANALYSIS = int(os.getenv('MAX_ROWS_FOR_ANALYSIS', 100000))
    
    @classmethod
    def get_db_config(cls, **kwargs) -> Dict[str, Any]:
        """
        데이터베이스 설정 반환
        
        Args:
            **kwargs: 사용자 정의 설정
            
        Returns:
            데이터베이스 설정 딕셔너리
        """
        config = cls.DEFAULT_DB_CONFIG.copy()
        config.update(kwargs)
        return config
    
    @classmethod
    def setup_logging(cls):
        """로깅 설정"""
        import logging
        
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT
        )


# 데이터 타입 매핑
POSTGRES_TYPE_MAPPING = {
    'integer': 'int64',
    'bigint': 'int64',
    'smallint': 'int32',
    'decimal': 'float64',
    'numeric': 'float64',
    'real': 'float32',
    'double precision': 'float64',
    'boolean': 'bool',
    'text': 'object',
    'varchar': 'object',
    'char': 'object',
    'date': 'datetime64[ns]',
    'timestamp': 'datetime64[ns]',
    'timestamptz': 'datetime64[ns]'
}

# 분석 컬럼 타입 분류
NUMERIC_TYPES = ['int64', 'int32', 'float64', 'float32']
CATEGORICAL_TYPES = ['object', 'category', 'bool']
DATETIME_TYPES = ['datetime64[ns]', 'datetime']

# 내보내기 형식 설정
EXPORT_FORMATS = {
    'csv': {
        'extension': '.csv',
        'encoding': 'utf-8-sig',
        'index': False
    },
    'excel': {
        'extension': '.xlsx',
        'engine': 'openpyxl',
        'index': False
    },
    'json': {
        'extension': '.json',
        'orient': 'records',
        'indent': 2
    },
    'parquet': {
        'extension': '.parquet',
        'engine': 'pyarrow',
        'index': False
    },
    'html': {
        'extension': '.html',
        'escape': False,
        'index': False
    }
}

# SQL 쿼리 템플릿
SQL_TEMPLATES = {
    'table_info': """
        SELECT 
            column_name, 
            data_type, 
            is_nullable, 
            column_default,
            character_maximum_length
        FROM information_schema.columns
        WHERE table_name = %s AND table_schema = 'public'
        ORDER BY ordinal_position;
    """,
    
    'table_size': """
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
            pg_total_relation_size(schemaname||'.'||tablename) as total_bytes,
            pg_relation_size(schemaname||'.'||tablename) as table_bytes
        FROM pg_tables 
        WHERE tablename = %s AND schemaname = 'public';
    """,
    
    'table_stats': """
        SELECT 
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples
        FROM pg_stat_user_tables 
        WHERE relname = %s;
    """,
    
    'index_info': """
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE tablename = %s AND schemaname = 'public';
    """
}

# 에러 메시지
ERROR_MESSAGES = {
    'connection_failed': '데이터베이스 연결에 실패했습니다.',
    'query_failed': '쿼리 실행에 실패했습니다.',
    'table_not_found': '지정된 테이블을 찾을 수 없습니다.',
    'invalid_data_type': '지원하지 않는 데이터 타입입니다.',
    'export_failed': '파일 내보내기에 실패했습니다.',
    'analysis_failed': '데이터 분석에 실패했습니다.',
    'memory_limit_exceeded': '메모리 사용량이 한계를 초과했습니다.'
}

# 성공 메시지
SUCCESS_MESSAGES = {
    'connection_established': '데이터베이스 연결이 성공적으로 설정되었습니다.',
    'query_executed': '쿼리가 성공적으로 실행되었습니다.',
    'data_exported': '데이터가 성공적으로 내보내졌습니다.',
    'analysis_completed': '데이터 분석이 완료되었습니다.',
    'backup_created': '백업이 성공적으로 생성되었습니다.'
}
