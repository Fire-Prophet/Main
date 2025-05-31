#!/usr/bin/env python3
"""
PostgreSQL 연결 사용 예제
"""

from db_connection import PostgreSQLConnection
import os

def format_table_name(table_name):
    """테이블 이름을 PostgreSQL 쿼리에 적합한 형태로 포맷팅"""
    # 대문자나 특수문자가 포함된 경우 따옴표로 감싸기
    if any(c.isupper() or not c.isalnum() and c != '_' for c in table_name):
        return f'"{table_name}"'
    return table_name

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

def example_detailed_table_analysis():
    """테이블 정보 세밀 분석 예제"""
    print("\n=== 테이블 세밀 분석 예제 ===")
    
    db = PostgreSQLConnection()
    
    if not db.connect():
        return
    
    try:
        # 1. 모든 테이블 목록과 기본 정보 조회
        print("\n1. 전체 테이블 개요:")
        table_overview_query = """
        SELECT 
            schemaname,
            tablename,
            tableowner,
            tablespace,
            hasindexes,
            hasrules,
            hastriggers,
            rowsecurity
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
        """
        
        tables_info = db.execute_query(table_overview_query)
        for table in tables_info:
            print(f"   📊 테이블: {table['tablename']}")
            print(f"      스키마: {table['schemaname']}")
            print(f"      소유자: {table['tableowner']}")
            print(f"      인덱스: {'있음' if table['hasindexes'] else '없음'}")
            print(f"      트리거: {'있음' if table['hastriggers'] else '없음'}")
            print("   ---")
        
        # 2. 사용자가 테이블 선택
        table_names = [table['tablename'] for table in tables_info]
        print(f"\n분석할 테이블을 선택하세요:")
        for i, name in enumerate(table_names, 1):
            print(f"   {i}. {name}")
        
        print(f"   0. 모든 테이블 간략 분석")
        print(f"   -1. 건너뛰기")
        
        try:
            choice = int(input("\n선택 (번호 입력): "))
            
            if choice == -1:
                print("테이블 분석을 건너뜁니다.")
                return
            elif choice == 0:
                # 모든 테이블 간략 분석
                analyze_all_tables_brief(db, table_names)
            elif 1 <= choice <= len(table_names):
                # 선택한 테이블 상세 분석
                selected_table = table_names[choice - 1]
                analyze_single_table_detailed(db, selected_table)
            else:
                print("잘못된 선택입니다.")
        
        except ValueError:
            print("숫자를 입력해주세요.")
    
    except Exception as e:
        print(f"테이블 분석 중 오류: {e}")
    
    finally:
        db.disconnect()

def analyze_all_tables_brief(db, table_names):
    """모든 테이블 간략 분석"""
    print("\n=== 모든 테이블 간략 분석 ===")
    
    for table_name in table_names:
        print(f"\n📋 테이블: {table_name}")
        
        # 레코드 수 조회
        try:
            formatted_name = format_table_name(table_name)
            count_query = f"SELECT COUNT(*) as record_count FROM {formatted_name}"
            count_result = db.execute_query(count_query)
            record_count = count_result[0]['record_count'] if count_result else 0
            print(f"   📊 레코드 수: {record_count:,}")
        except Exception as e:
            print(f"   ❌ 레코드 수 조회 실패: {e}")
        
        # 컬럼 수 조회
        try:
            columns = db.get_table_info(table_name)
            print(f"   📊 컬럼 수: {len(columns)}")
            
            # 데이터 타입별 컬럼 수
            type_counts = {}
            for col in columns:
                data_type = col['data_type']
                type_counts[data_type] = type_counts.get(data_type, 0) + 1
            
            print(f"   📊 데이터 타입별 컬럼:")
            for dtype, count in sorted(type_counts.items()):
                print(f"      - {dtype}: {count}개")
        
        except Exception as e:
            print(f"   ❌ 컬럼 정보 조회 실패: {e}")
        
        print("   " + "─" * 50)

def analyze_single_table_detailed(db, table_name):
    """단일 테이블 상세 분석"""
    print(f"\n=== 테이블 '{table_name}' 상세 분석 ===")
    
    formatted_name = format_table_name(table_name)
    
    try:
        # 1. 기본 테이블 정보
        print("\n1. 기본 정보:")
        basic_info_query = f"""
        SELECT 
            pg_size_pretty(pg_total_relation_size({formatted_name})) as total_size,
            pg_size_pretty(pg_relation_size({formatted_name})) as table_size,
            pg_size_pretty(pg_total_relation_size({formatted_name}) - pg_relation_size({formatted_name})) as index_size
        """
        
        size_info = db.execute_query(basic_info_query)
        if size_info:
            info = size_info[0]
            print(f"   📊 총 크기: {info['total_size']}")
            print(f"   📊 테이블 크기: {info['table_size']}")
            print(f"   📊 인덱스 크기: {info['index_size']}")
        
        # 2. 레코드 수
        count_query = f"SELECT COUNT(*) as record_count FROM {formatted_name}"
        count_result = db.execute_query(count_query)
        record_count = count_result[0]['record_count'] if count_result else 0
        print(f"   📊 레코드 수: {record_count:,}")
        
        # 3. 컬럼 상세 정보
        print("\n2. 컬럼 상세 정보:")
        columns = db.get_table_info(table_name)
        
        print(f"   📊 총 컬럼 수: {len(columns)}")
        print("\n   컬럼 목록:")
        for i, col in enumerate(columns, 1):
            nullable = "NULL 허용" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" (기본값: {col['column_default']})" if col['column_default'] else ""
            print(f"   {i:2d}. {col['column_name']:20} | {col['data_type']:20} | {nullable}{default}")
        
        # 4. 인덱스 정보
        print("\n3. 인덱스 정보:")
        index_query = f"""
        SELECT 
            indexname,
            indexdef,
            pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
        FROM pg_indexes 
        WHERE tablename = '{table_name}'
        ORDER BY indexname
        """
        
        indexes = db.execute_query(index_query)
        if indexes:
            for idx in indexes:
                print(f"   🔍 인덱스: {idx['indexname']}")
                print(f"      크기: {idx['index_size']}")
                print(f"      정의: {idx['indexdef']}")
                print("   ---")
        else:
            print("   인덱스가 없습니다.")
        
        # 5. 제약조건 정보
        print("\n4. 제약조건 정보:")
        constraints_query = f"""
        SELECT 
            conname as constraint_name,
            contype as constraint_type,
            pg_get_constraintdef(oid) as constraint_definition
        FROM pg_constraint 
        WHERE conrelid = {formatted_name}::regclass
        ORDER BY contype, conname
        """
        
        constraints = db.execute_query(constraints_query)
        if constraints:
            constraint_types = {
                'p': 'PRIMARY KEY',
                'f': 'FOREIGN KEY', 
                'u': 'UNIQUE',
                'c': 'CHECK',
                'n': 'NOT NULL'
            }
            
            for constraint in constraints:
                ctype = constraint_types.get(constraint['constraint_type'], constraint['constraint_type'])
                print(f"   🔒 {ctype}: {constraint['constraint_name']}")
                print(f"      정의: {constraint['constraint_definition']}")
                print("   ---")
        else:
            print("   제약조건이 없습니다.")
        
        # 6. 공간 데이터 정보 (PostGIS)
        print("\n5. 공간 데이터 정보:")
        spatial_info_query = f"""
        SELECT 
            f_geometry_column as geom_column,
            coord_dimension as dimensions,
            srid,
            type as geometry_type
        FROM geometry_columns 
        WHERE f_table_name = '{table_name}'
        """
        
        spatial_info = db.execute_query(spatial_info_query)
        if spatial_info:
            for geom in spatial_info:
                print(f"   🌍 지오메트리 컬럼: {geom['geom_column']}")
                print(f"      타입: {geom['geometry_type']}")
                print(f"      차원: {geom['dimensions']}D")
                print(f"      SRID: {geom['srid']}")
                print("   ---")
                
                # 공간 데이터 범위 조회
                extent_query = f"""
                SELECT 
                    ST_XMin(ST_Extent({geom['geom_column']})) as min_x,
                    ST_YMin(ST_Extent({geom['geom_column']})) as min_y,
                    ST_XMax(ST_Extent({geom['geom_column']})) as max_x,
                    ST_YMax(ST_Extent({geom['geom_column']})) as max_y
                FROM {formatted_name}
                WHERE {geom['geom_column']} IS NOT NULL
                """
                
                extent_result = db.execute_query(extent_query)
                if extent_result and extent_result[0]['min_x']:
                    extent = extent_result[0]
                    print(f"   📍 공간 범위:")
                    print(f"      X: {extent['min_x']:.6f} ~ {extent['max_x']:.6f}")
                    print(f"      Y: {extent['min_y']:.6f} ~ {extent['max_y']:.6f}")
        else:
            print("   공간 데이터가 없습니다.")
        
        # 7. 샘플 데이터 미리보기
        print("\n6. 샘플 데이터 미리보기 (상위 3개 레코드):")
        if record_count > 0:
            sample_query = f'SELECT * FROM {formatted_name} LIMIT 3'
            sample_data = db.execute_query(sample_query)
            
            if sample_data:
                for i, row in enumerate(sample_data, 1):
                    print(f"   레코드 {i}:")
                    for key, value in row.items():
                        # 값이 너무 길면 자르기
                        if isinstance(value, str) and len(str(value)) > 50:
                            display_value = str(value)[:47] + "..."
                        else:
                            display_value = value
                        print(f"      {key}: {display_value}")
                    print("   ---")
        else:
            print("   데이터가 없습니다.")
    
    except Exception as e:
        print(f"상세 분석 중 오류: {e}")

def example_table_statistics():
    """테이블 통계 정보 조회"""
    print("\n=== 데이터베이스 통계 정보 ===")
    
    db = PostgreSQLConnection()
    
    if not db.connect():
        return
    
    try:
        # 1. 데이터베이스 전체 통계
        print("\n1. 데이터베이스 전체 통계:")
        db_stats_query = """
        SELECT 
            COUNT(*) as total_tables,
            SUM(pg_total_relation_size('"' || tablename || '"')) as total_size
        FROM pg_tables 
        WHERE schemaname = 'public'
        """
        
        stats = db.execute_query(db_stats_query)
        if stats:
            stat = stats[0]
            print(f"   📊 총 테이블 수: {stat['total_tables']}")
            if stat['total_size']:
                # 바이트를 읽기 쉬운 형태로 변환
                size_query = f"SELECT pg_size_pretty({stat['total_size']}) as readable_size"
                size_result = db.execute_query(size_query)
                if size_result:
                    print(f"   📊 총 데이터베이스 크기: {size_result[0]['readable_size']}")
        
        # 2. 테이블별 크기 순위
        print("\n2. 테이블 크기 순위 (상위 10개):")
        size_ranking_query = """
        SELECT 
            tablename,
            pg_size_pretty(pg_total_relation_size('"' || tablename || '"')) as total_size,
            pg_size_pretty(pg_relation_size('"' || tablename || '"')) as table_size,
            pg_total_relation_size('"' || tablename || '"') as size_bytes
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size('"' || tablename || '"') DESC
        LIMIT 10
        """
        
        size_ranking = db.execute_query(size_ranking_query)
        if size_ranking:
            for i, table in enumerate(size_ranking, 1):
                print(f"   {i:2d}. {table['tablename']:30} | 총크기: {table['total_size']:>10} | 테이블: {table['table_size']:>10}")
        
        # 3. 공간 테이블 통계
        print("\n3. 공간 테이블 통계:")
        spatial_stats_query = """
        SELECT 
            COUNT(*) as spatial_table_count,
            COUNT(DISTINCT srid) as unique_srid_count,
            array_agg(DISTINCT type) as geometry_types
        FROM geometry_columns
        """
        
        spatial_stats = db.execute_query(spatial_stats_query)
        if spatial_stats and spatial_stats[0]['spatial_table_count'] > 0:
            stats = spatial_stats[0]
            print(f"   🌍 공간 테이블 수: {stats['spatial_table_count']}")
            print(f"   🌍 사용된 SRID 종류: {stats['unique_srid_count']}")
            print(f"   🌍 지오메트리 타입: {', '.join(stats['geometry_types']) if stats['geometry_types'] else 'None'}")
        else:
            print("   공간 테이블이 없습니다.")
    
    except Exception as e:
        print(f"통계 조회 중 오류: {e}")
    
    finally:
        db.disconnect()

def main():
    """메인 함수"""
    print("PostgreSQL 연결 예제 프로그램")
    print("=" * 40)
    
    while True:
        print("\n🔍 메뉴를 선택하세요:")
        print("1. 기본 연결 테스트")
        print("2. 공간 데이터 쿼리")
        print("3. 테이블 세밀 분석")
        print("4. 데이터베이스 통계")
        print("5. 샘플 테이블 생성")
        print("0. 종료")
        
        try:
            choice = input("\n선택 (0-5): ").strip()
            
            if choice == '0':
                print("프로그램을 종료합니다.")
                break
            elif choice == '1':
                example_basic_usage()
            elif choice == '2':
                example_spatial_queries()
            elif choice == '3':
                example_detailed_table_analysis()
            elif choice == '4':
                example_table_statistics()
            elif choice == '5':
                print("\n샘플 테이블을 생성하시겠습니까? (y/n): ", end="")
                response = input().lower().strip()
                if response in ['y', 'yes', '예']:
                    example_create_sample_table()
            else:
                print("❌ 잘못된 선택입니다. 0-5 사이의 숫자를 입력하세요.")
        
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
