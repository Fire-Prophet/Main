#!/usr/bin/env python3
"""
PostgreSQL 연결 사용 예제
"""

from db_connection import PostgreSQLConnection
import os

def example_basic_usage():
    """기본 사용법 예제"""
    print("=== PostgreSQL 기본 연결 예제 ===")
    
    # 데이터베이스 연결
    db = PostgreSQLConnection()
    
    if not db.connect():
        print("연결 실패!")
        return
    
    try:
        # 1. 기본 정보 조회
        print("\n1. 데이터베이스 기본 정보:")
        info_query = """
        SELECT 
            current_database() as database_name,
            current_user as user_name,
            version() as postgres_version,
            now() as current_time
        """
        results = db.execute_query(info_query)
        if results:
            info = results[0]
            for key, value in info.items():
                print(f"   {key}: {value}")
        
        # 2. 테이블 목록 조회
        print("\n2. 데이터베이스 테이블 목록:")
        tables = db.get_table_list()
        if tables:
            for i, table in enumerate(tables, 1):
                print(f"   {i}. {table}")
        else:
            print("   테이블이 없습니다.")
        
        # 3. 공간 확장 기능 확인 (PostGIS)
        print("\n3. PostGIS 확장 기능 확인:")
        postgis_query = """
        SELECT EXISTS(
            SELECT 1 FROM pg_extension WHERE extname = 'postgis'
        ) as postgis_installed
        """
        results = db.execute_query(postgis_query)
        if results:
            if results[0]['postgis_installed']:
                print("   PostGIS가 설치되어 있습니다.")
                
                # PostGIS 버전 확인
                version_query = "SELECT PostGIS_Version() as postgis_version"
                version_result = db.execute_query(version_query)
                if version_result:
                    print(f"   PostGIS 버전: {version_result[0]['postgis_version']}")
            else:
                print("   PostGIS가 설치되어 있지 않습니다.")
    
    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        db.disconnect()

def example_spatial_queries():
    """공간 데이터 쿼리 예제 (PostGIS가 있는 경우)"""
    print("\n=== 공간 데이터 쿼리 예제 ===")
    
    db = PostgreSQLConnection()
    
    if not db.connect():
        return
    
    try:
        # 공간 테이블 찾기
        spatial_tables_query = """
        SELECT 
            f_table_name as table_name,
            f_geometry_column as geom_column,
            type as geometry_type,
            srid
        FROM geometry_columns
        ORDER BY f_table_name
        """
        
        spatial_tables = db.execute_query(spatial_tables_query)
        
        if spatial_tables:
            print("공간 데이터 테이블:")
            for table in spatial_tables:
                print(f"   테이블: {table['table_name']}")
                print(f"   지오메트리 컬럼: {table['geom_column']}")
                print(f"   지오메트리 타입: {table['geometry_type']}")
                print(f"   SRID: {table['srid']}")
                print("   ---")
        else:
            print("공간 데이터 테이블이 없습니다.")
    
    except Exception as e:
        print(f"공간 쿼리 실행 중 오류: {e}")
    
    finally:
        db.disconnect()

def example_create_sample_table():
    """샘플 테이블 생성 예제"""
    print("\n=== 샘플 테이블 생성 예제 ===")
    
    db = PostgreSQLConnection()
    
    if not db.connect():
        return
    
    try:
        # 샘플 테이블 생성
        create_table_query = """
        CREATE TABLE IF NOT EXISTS sample_locations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        if db.execute_command(create_table_query):
            print("샘플 테이블이 생성되었습니다.")
            
            # 샘플 데이터 삽입
            sample_data = [
                ("서울시청", "서울특별시 중구 태평로1가", 37.5663174, 126.9779451),
                ("부산시청", "부산광역시 연제구 중앙대로", 35.1796, 129.0756),
                ("대구시청", "대구광역시 중구 공평로", 35.8714, 128.6014),
            ]
            
            insert_query = """
            INSERT INTO sample_locations (name, description, latitude, longitude)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """
            
            for data in sample_data:
                db.execute_command(insert_query, data)
            
            print("샘플 데이터가 삽입되었습니다.")
            
            # 삽입된 데이터 조회
            select_query = "SELECT * FROM sample_locations ORDER BY id"
            results = db.execute_query(select_query)
            
            print("\n삽입된 데이터:")
            for row in results:
                print(f"   ID: {row['id']}, 이름: {row['name']}, "
                      f"위치: ({row['latitude']}, {row['longitude']})")
    
    except Exception as e:
        print(f"테이블 생성 중 오류: {e}")
    
    finally:
        db.disconnect()

def main():
    """메인 함수"""
    print("PostgreSQL 연결 예제 프로그램")
    print("=" * 40)
    
    # 1. 기본 사용법
    example_basic_usage()
    
    # 2. 공간 데이터 쿼리 (PostGIS)
    example_spatial_queries()
    
    # 3. 샘플 테이블 생성
    print("\n샘플 테이블을 생성하시겠습니까? (y/n): ", end="")
    response = input().lower().strip()
    if response in ['y', 'yes', '예']:
        example_create_sample_table()

if __name__ == "__main__":
    main()
