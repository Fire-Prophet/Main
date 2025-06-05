#!/usr/bin/env python3
"""
PostgreSQL Database Manager
데이터베이스 연결 및 기본 작업을 위한 통합 클래스
"""

import psycopg2
import psycopg2.extras
from psycopg2 import sql
import logging
from typing import List, Dict, Any, Optional, Union
import os
from contextlib import contextmanager
import pandas as pd


class PostgreSQLManager:
    """PostgreSQL 데이터베이스 관리 클래스"""
    
    def __init__(self, host: str = "123.212.210.230", port: int = 5432, 
                 user: str = "postgres", database: str = "gis_db", password: str = None):
        """
        PostgreSQL 연결 초기화
        
        Args:
            host: 데이터베이스 호스트
            port: 포트 번호
            user: 사용자명
            database: 데이터베이스명
            password: 비밀번호 (환경변수 또는 입력으로 받음)
        """
        self.host = host
        self.port = port
        self.user = user
        self.database = database
        self.password = password or os.getenv('POSTGRES_PASSWORD')
        self.connection = None
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """데이터베이스에 연결"""
        try:
            if not self.password:
                self.password = input("PostgreSQL 비밀번호를 입력하세요: ")
            
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.logger.info(f"데이터베이스에 성공적으로 연결되었습니다: {self.database}")
            return True
            
        except psycopg2.Error as e:
            self.logger.error(f"데이터베이스 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """데이터베이스 연결 종료"""
        if self.connection:
            self.connection.close()
            self.logger.info("데이터베이스 연결이 종료되었습니다.")
    
    @contextmanager
    def get_cursor(self, cursor_factory=None):
        """커서 컨텍스트 매니저"""
        if not self.connection:
            raise Exception("데이터베이스에 연결되지 않았습니다.")
        
        cursor = self.connection.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"쿼리 실행 중 오류 발생: {e}")
            raise
        else:
            self.connection.commit()
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: Union[tuple, dict] = None) -> List[Dict[str, Any]]:
        """SELECT 쿼리 실행"""
        try:
            with self.get_cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except psycopg2.Error as e:
            self.logger.error(f"쿼리 실행 실패: {e}")
            return []
    
    def execute_command(self, command: str, params: Union[tuple, dict] = None) -> bool:
        """INSERT, UPDATE, DELETE 명령 실행"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(command, params)
                self.logger.info(f"명령이 성공적으로 실행되었습니다. 영향받은 행: {cursor.rowcount}")
                return True
                
        except psycopg2.Error as e:
            self.logger.error(f"명령 실행 실패: {e}")
            return False
    
    def execute_many(self, command: str, params_list: List[Union[tuple, dict]]) -> bool:
        """배치 INSERT/UPDATE 실행"""
        try:
            with self.get_cursor() as cursor:
                cursor.executemany(command, params_list)
                self.logger.info(f"배치 명령이 성공적으로 실행되었습니다. 영향받은 행: {cursor.rowcount}")
                return True
                
        except psycopg2.Error as e:
            self.logger.error(f"배치 명령 실행 실패: {e}")
            return False
    
    def get_tables(self) -> List[str]:
        """데이터베이스의 모든 테이블 목록 조회"""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        results = self.execute_query(query)
        return [row['table_name'] for row in results]
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """특정 테이블의 컬럼 정보 조회"""
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
        """
        return self.execute_query(query, (table_name,))
    
    def get_table_size(self, table_name: str) -> Dict[str, Any]:
        """테이블 크기 정보 조회"""
        query = """
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
            pg_total_relation_size(schemaname||'.'||tablename) as total_bytes,
            pg_relation_size(schemaname||'.'||tablename) as table_bytes
        FROM pg_tables 
        WHERE tablename = %s AND schemaname = 'public';
        """
        results = self.execute_query(query, (table_name,))
        return results[0] if results else {}
    
    def get_row_count(self, table_name: str) -> int:
        """테이블 행 개수 조회"""
        query = f'SELECT COUNT(*) as count FROM "{table_name}";'
        results = self.execute_query(query)
        return results[0]['count'] if results else 0
    
    def to_dataframe(self, query: str, params: Union[tuple, dict] = None) -> pd.DataFrame:
        """쿼리 결과를 pandas DataFrame으로 반환"""
        try:
            if not self.connection:
                raise Exception("데이터베이스에 연결되지 않았습니다.")
            
            return pd.read_sql(query, self.connection, params=params)
            
        except Exception as e:
            self.logger.error(f"DataFrame 생성 실패: {e}")
            return pd.DataFrame()
    
    def from_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append') -> bool:
        """pandas DataFrame을 테이블에 저장"""
        try:
            if not self.connection:
                raise Exception("데이터베이스에 연결되지 않았습니다.")
            
            df.to_sql(table_name, self.connection, if_exists=if_exists, index=False)
            self.logger.info(f"DataFrame이 {table_name} 테이블에 저장되었습니다.")
            return True
            
        except Exception as e:
            self.logger.error(f"DataFrame 저장 실패: {e}")
            return False
    
    def test_connection(self) -> bool:
        """연결 테스트"""
        try:
            result = self.execute_query("SELECT version();")
            if result:
                self.logger.info(f"PostgreSQL 버전: {result[0]['version']}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"연결 테스트 실패: {e}")
            return False
    
    def create_backup(self, table_name: str) -> str:
        """테이블 백업 생성"""
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        backup_table = f"{table_name}_backup_{timestamp}"
        
        query = f'CREATE TABLE "{backup_table}" AS SELECT * FROM "{table_name}";'
        
        if self.execute_command(query):
            self.logger.info(f"백업 테이블 생성됨: {backup_table}")
            return backup_table
        else:
            self.logger.error("백업 생성 실패")
            return ""
    
    def __enter__(self):
        """Context manager 진입"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.disconnect()
