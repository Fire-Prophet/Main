#!/usr/bin/env python3
"""
PostgreSQL Database Connection Module
데이터베이스 연결 및 기본 작업을 위한 모듈
"""

import psycopg2
import psycopg2.extras
from psycopg2 import sql
import logging
from typing import List, Dict, Any, Optional
import os
from contextlib import contextmanager

class PostgreSQLConnection:
    """PostgreSQL 데이터베이스 연결 클래스"""
    
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
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """SELECT 쿼리 실행"""
        try:
            with self.get_cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except psycopg2.Error as e:
            self.logger.error(f"쿼리 실행 실패: {e}")
            return []
    
    def execute_command(self, command: str, params: tuple = None) -> bool:
        """INSERT, UPDATE, DELETE 명령 실행"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(command, params)
                self.logger.info(f"명령이 성공적으로 실행되었습니다. 영향받은 행: {cursor.rowcount}")
                return True
                
        except psycopg2.Error as e:
            self.logger.error(f"명령 실행 실패: {e}")
            return False
    
    def get_table_list(self) -> List[str]:
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


def main():
    """메인 함수 - 사용 예제"""
    # 데이터베이스 연결 인스턴스 생성
    db = PostgreSQLConnection()
    
    # 연결 시도
    if not db.connect():
        print("데이터베이스 연결에 실패했습니다.")
        return
    
    try:
        # 연결 테스트
        print("\n=== 연결 테스트 ===")
        db.test_connection()
        
        # 테이블 목록 조회
        print("\n=== 테이블 목록 ===")
        tables = db.get_table_list()
        for table in tables:
            print(f"- {table}")
        
        # 첫 번째 테이블의 정보 조회 (테이블이 있는 경우)
        if tables:
            table_name = tables[0]
            print(f"\n=== '{table_name}' 테이블 정보 ===")
            columns = db.get_table_info(table_name)
            for col in columns:
                print(f"- {col['column_name']}: {col['data_type']} "
                      f"(NULL 허용: {col['is_nullable']})")
        
        # 샘플 쿼리 실행 (예제)
        print("\n=== 샘플 쿼리 실행 ===")
        sample_query = "SELECT current_database(), current_user, now();"
        results = db.execute_query(sample_query)
        if results:
            result = results[0]
            print(f"현재 데이터베이스: {result['current_database']}")
            print(f"현재 사용자: {result['current_user']}")
            print(f"현재 시간: {result['now']}")
    
    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        # 연결 종료
        db.disconnect()


if __name__ == "__main__":
    main()
