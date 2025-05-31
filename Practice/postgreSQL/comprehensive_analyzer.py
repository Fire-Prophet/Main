#!/usr/bin/env python3
"""
PostgreSQL 데이터베이스 종합 분석 도구
테이블 분석, 데이터 품질 검사, 데이터 내보내기 기능을 통합한 메인 인터페이스
"""

from db_connection import PostgreSQLConnection
from table_analyzer import PostgreSQLTableAnalyzer
from data_quality_checker import PostgreSQLDataQualityChecker
from data_exporter import PostgreSQLDataExporter
import sys
import os

class PostgreSQLComprehensiveAnalyzer:
    """PostgreSQL 종합 분석기"""
    
    def __init__(self):
        self.db = PostgreSQLConnection()
        self.table_analyzer = PostgreSQLTableAnalyzer()
        self.quality_checker = PostgreSQLDataQualityChecker()
        self.data_exporter = PostgreSQLDataExporter()
    
    def connect(self):
        """데이터베이스 연결"""
        if not self.db.connect():
            return False
        
        # 각 모듈에 연결 공유
        self.table_analyzer.db = self.db
        self.quality_checker.db = self.db
        self.data_exporter.db = self.db
        
        return True
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        self.db.disconnect()
    
    def show_main_menu(self):
        """메인 메뉴 표시"""
        print(f"\n{'='*60}")
        print("🔍 PostgreSQL 데이터베이스 종합 분석 도구")
        print(f"{'='*60}")
        print("1. 📊 테이블 상세 분석")
        print("2. 🔍 데이터 품질 검사")
        print("3. 📁 데이터 내보내기")
        print("4. 📋 데이터베이스 정보")
        print("5. 🔄 공간 데이터 분석")
        print("6. 📈 성능 모니터링")
        print("0. 🚪 종료")
        print(f"{'='*60}")
    
    def get_table_list(self):
        """테이블 목록 조회 및 선택"""
        try:
            tables_query = """
            SELECT 
                t.tablename,
                pg_size_pretty(pg_total_relation_size(quote_ident(t.tablename))) as total_size,
                c.reltuples::bigint as estimated_rows
            FROM pg_tables t
            LEFT JOIN pg_class c ON c.relname = t.tablename
            WHERE t.schemaname = 'public'
            ORDER BY pg_total_relation_size(quote_ident(t.tablename)) DESC
            """
            
            tables = self.db.execute_query(tables_query)
            
            if not tables:
                print("⚠️  테이블을 찾을 수 없습니다.")
                return None
            
            print("\n📋 사용 가능한 테이블:")
            for i, table in enumerate(tables, 1):
                rows = f"{table['estimated_rows']:,}" if table['estimated_rows'] else "Unknown"
                print(f"   {i:2d}. {table['tablename']} ({table['total_size']}, ~{rows} rows)")
            
            while True:
                try:
                    choice = input(f"\n테이블 번호를 선택하세요 (1-{len(tables)}, 0=뒤로): ").strip()
                    
                    if choice == '0':
                        return None
                    
                    table_index = int(choice) - 1
                    if 0 <= table_index < len(tables):
                        return tables[table_index]['tablename']
                    else:
                        print("❌ 잘못된 번호입니다.")
                        
                except ValueError:
                    print("❌ 숫자를 입력해주세요.")
                except KeyboardInterrupt:
                    return None
                    
        except Exception as e:
            print(f"❌ 테이블 목록 조회 실패: {e}")
            return None
    
    def detailed_table_analysis(self):
        """상세 테이블 분석"""
        print("\n🔍 테이블 상세 분석")
        table_name = self.get_table_list()
        
        if table_name:
            self.table_analyzer.analyze_table_comprehensive(table_name)
            
            # 분석 결과 저장 옵션
            save_choice = input("\n분석 결과를 파일로 저장하시겠습니까? (y/n): ").lower().strip()
            if save_choice in ['y', 'yes', '예']:
                try:
                    # 분석 데이터 수집
                    analysis_data = {
                        'basic_info': self.table_analyzer.get_all_tables(),
                        'columns': self.table_analyzer.get_table_columns_detailed(table_name),
                        'indexes': self.table_analyzer.get_table_indexes(table_name),
                        'constraints': self.table_analyzer.get_table_constraints(table_name),
                        'spatial_info': self.table_analyzer.get_spatial_info(table_name)
                    }
                    
                    saved_file = self.data_exporter.export_analysis_report(table_name, analysis_data)
                    if saved_file:
                        print(f"💾 분석 결과가 저장되었습니다!")
                        
                except Exception as e:
                    print(f"❌ 파일 저장 실패: {e}")
    
    def data_quality_check(self):
        """데이터 품질 검사"""
        print("\n🔍 데이터 품질 검사")
        table_name = self.get_table_list()
        
        if table_name:
            results = self.quality_checker.comprehensive_quality_check(table_name)
            self.quality_checker.print_quality_report(results)
            
            # 품질 보고서 저장 옵션
            save_choice = input("\n품질 보고서를 파일로 저장하시겠습니까? (y/n): ").lower().strip()
            if save_choice in ['y', 'yes', '예']:
                try:
                    saved_file = self.data_exporter.export_analysis_report(f"{table_name}_quality", results)
                    if saved_file:
                        print(f"💾 품질 보고서가 저장되었습니다!")
                except Exception as e:
                    print(f"❌ 파일 저장 실패: {e}")
    
    def data_export_menu(self):
        """데이터 내보내기 메뉴"""
        print("\n📁 데이터 내보내기")
        table_name = self.get_table_list()
        
        if not table_name:
            return
        
        print(f"\n테이블 '{table_name}' 내보내기 옵션:")
        print("1. 📄 CSV 형식으로 내보내기")
        print("2. 📋 JSON 형식으로 내보내기")
        print("3. 🌍 GeoJSON 형식으로 내보내기 (공간 데이터)")
        print("0. 뒤로")
        
        export_choice = input("\n내보내기 형식을 선택하세요: ").strip()
        
        # 제한 조건 설정
        limit_choice = input("내보낼 레코드 수를 제한하시겠습니까? (숫자 입력 또는 Enter로 전체): ").strip()
        limit = None
        if limit_choice.isdigit():
            limit = int(limit_choice)
        
        where_clause = input("WHERE 조건을 추가하시겠습니까? (조건 입력 또는 Enter로 생략): ").strip()
        if not where_clause:
            where_clause = None
        
        try:
            if export_choice == '1':
                self.data_exporter.export_table_to_csv(table_name, limit, where_clause)
            elif export_choice == '2':
                self.data_exporter.export_table_to_json(table_name, limit, where_clause)
            elif export_choice == '3':
                # 공간 컬럼 찾기
                spatial_info = self.table_analyzer.get_spatial_info(table_name)
                if spatial_info:
                    geom_column = spatial_info[0]['geom_column']
                    self.data_exporter.export_spatial_data_to_geojson(table_name, geom_column, limit)
                else:
                    print("⚠️  이 테이블에는 공간 데이터가 없습니다.")
            
        except Exception as e:
            print(f"❌ 데이터 내보내기 실패: {e}")
    
    def database_info(self):
        """데이터베이스 정보"""
        print("\n📋 데이터베이스 정보")
        
        try:
            # 데이터베이스 기본 정보
            db_info_query = """
            SELECT 
                current_database() as database_name,
                version() as version,
                current_user as current_user,
                inet_server_addr() as server_ip,
                inet_server_port() as server_port
            """
            
            db_info = self.db.execute_query(db_info_query)
            
            if db_info:
                info = db_info[0]
                print(f"\n🏛️  데이터베이스 기본 정보:")
                print(f"   • 데이터베이스명: {info['database_name']}")
                print(f"   • 버전: {info['version']}")
                print(f"   • 현재 사용자: {info['current_user']}")
                print(f"   • 서버 IP: {info['server_ip']}")
                print(f"   • 서버 포트: {info['server_port']}")
            
            # 확장 기능 정보
            extensions_query = """
            SELECT extname, extversion
            FROM pg_extension
            ORDER BY extname
            """
            
            extensions = self.db.execute_query(extensions_query)
            
            if extensions:
                print(f"\n🔧 설치된 확장 기능:")
                for ext in extensions:
                    print(f"   • {ext['extname']} (v{ext['extversion']})")
            
            # 데이터베이스 크기 정보
            size_query = """
            SELECT 
                pg_size_pretty(pg_database_size(current_database())) as database_size,
                count(*) as total_tables
            FROM pg_tables 
            WHERE schemaname = 'public'
            """
            
            size_info = self.db.execute_query(size_query)
            
            if size_info:
                size = size_info[0]
                print(f"\n📊 데이터베이스 크기 정보:")
                print(f"   • 데이터베이스 크기: {size['database_size']}")
                print(f"   • 총 테이블 수: {size['total_tables']}")
            
        except Exception as e:
            print(f"❌ 데이터베이스 정보 조회 실패: {e}")
    
    def spatial_data_analysis(self):
        """공간 데이터 분석"""
        print("\n🌍 공간 데이터 분석")
        
        try:
            # 공간 테이블 찾기
            spatial_tables_query = """
            SELECT 
                f_table_name as table_name,
                f_geometry_column as geom_column,
                type as geometry_type,
                srid,
                coord_dimension as dimensions
            FROM geometry_columns
            ORDER BY f_table_name
            """
            
            spatial_tables = self.db.execute_query(spatial_tables_query)
            
            if not spatial_tables:
                print("⚠️  공간 데이터 테이블을 찾을 수 없습니다.")
                return
            
            print(f"\n🗺️  공간 데이터 테이블:")
            for i, table in enumerate(spatial_tables, 1):
                print(f"   {i}. {table['table_name']} - {table['geometry_type']} (SRID: {table['srid']})")
            
            choice = input(f"\n분석할 테이블 번호를 선택하세요 (1-{len(spatial_tables)}, 0=뒤로): ").strip()
            
            if choice == '0':
                return
            
            table_index = int(choice) - 1
            if 0 <= table_index < len(spatial_tables):
                selected_table = spatial_tables[table_index]
                table_name = selected_table['table_name']
                geom_column = selected_table['geom_column']
                
                print(f"\n🔍 '{table_name}' 테이블 공간 분석:")
                
                # 공간 범위 조회
                extent = self.table_analyzer.get_spatial_extent(table_name, geom_column)
                if extent:
                    ext = extent[0]
                    print(f"   📐 공간 범위:")
                    print(f"      X: {ext['min_x']} ~ {ext['max_x']}")
                    print(f"      Y: {ext['min_y']} ~ {ext['max_y']}")
                    print(f"      중심점: ({ext['center_x']}, {ext['center_y']})")
                
                # 기하 통계
                geom_stats_query = f"""
                SELECT 
                    COUNT(*) as total_features,
                    COUNT("{geom_column}") as features_with_geometry,
                    COUNT(*) - COUNT("{geom_column}") as features_without_geometry,
                    AVG(ST_Area("{geom_column}")) as avg_area,
                    AVG(ST_Perimeter("{geom_column}")) as avg_perimeter
                FROM "{table_name}"
                """
                
                stats = self.db.execute_query(geom_stats_query)
                if stats:
                    stat = stats[0]
                    print(f"\n   📊 기하 통계:")
                    print(f"      총 피처 수: {stat['total_features']:,}")
                    print(f"      기하 데이터 보유: {stat['features_with_geometry']:,}")
                    print(f"      기하 데이터 없음: {stat['features_without_geometry']:,}")
                    if stat['avg_area']:
                        print(f"      평균 면적: {float(stat['avg_area']):.2f}")
                    if stat['avg_perimeter']:
                        print(f"      평균 둘레: {float(stat['avg_perimeter']):.2f}")
            
        except Exception as e:
            print(f"❌ 공간 데이터 분석 실패: {e}")
    
    def performance_monitoring(self):
        """성능 모니터링"""
        print("\n📈 성능 모니터링")
        
        try:
            # 테이블별 활동 통계
            activity_query = """
            SELECT 
                schemaname,
                tablename,
                seq_scan,
                seq_tup_read,
                idx_scan,
                idx_tup_fetch,
                n_tup_ins,
                n_tup_upd,
                n_tup_del,
                n_live_tup,
                n_dead_tup,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
            ORDER BY seq_scan + COALESCE(idx_scan, 0) DESC
            LIMIT 10
            """
            
            activities = self.db.execute_query(activity_query)
            
            if activities:
                print(f"\n📊 상위 10개 테이블 활동 통계:")
                print(f"{'테이블명':<20} {'시퀀스스캔':<10} {'인덱스스캔':<10} {'라이브투플':<10} {'데드투플':<10}")
                print("-" * 70)
                
                for activity in activities:
                    print(f"{activity['tablename']:<20} "
                          f"{activity['seq_scan'] or 0:<10} "
                          f"{activity['idx_scan'] or 0:<10} "
                          f"{activity['n_live_tup'] or 0:<10} "
                          f"{activity['n_dead_tup'] or 0:<10}")
            
            # 인덱스 사용 통계
            index_usage_query = """
            SELECT 
                t.tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size
            FROM pg_stat_user_indexes i
            JOIN pg_stat_user_tables t ON i.relid = t.relid
            WHERE t.schemaname = 'public'
            ORDER BY idx_scan DESC NULLS LAST
            LIMIT 10
            """
            
            index_stats = self.db.execute_query(index_usage_query)
            
            if index_stats:
                print(f"\n🔍 상위 10개 인덱스 사용 통계:")
                print(f"{'테이블명':<20} {'인덱스명':<25} {'스캔횟수':<10} {'크기':<10}")
                print("-" * 75)
                
                for idx in index_stats:
                    print(f"{idx['tablename']:<20} "
                          f"{idx['indexname']:<25} "
                          f"{idx['idx_scan'] or 0:<10} "
                          f"{idx['index_size']:<10}")
            
            # 연결 정보
            connections_query = """
            SELECT 
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections
            FROM pg_stat_activity
            """
            
            conn_stats = self.db.execute_query(connections_query)
            
            if conn_stats:
                conn = conn_stats[0]
                print(f"\n🔗 연결 통계:")
                print(f"   • 총 연결 수: {conn['total_connections']}")
                print(f"   • 활성 연결 수: {conn['active_connections']}")
                print(f"   • 유휴 연결 수: {conn['idle_connections']}")
            
        except Exception as e:
            print(f"❌ 성능 모니터링 실패: {e}")
    
    def run(self):
        """메인 실행 함수"""
        if not self.connect():
            print("❌ 데이터베이스 연결 실패!")
            return
        
        try:
            print("✅ 데이터베이스 연결 성공!")
            
            while True:
                self.show_main_menu()
                
                try:
                    choice = input("\n메뉴를 선택하세요: ").strip()
                    
                    if choice == '0':
                        print("\n👋 프로그램을 종료합니다.")
                        break
                    elif choice == '1':
                        self.detailed_table_analysis()
                    elif choice == '2':
                        self.data_quality_check()
                    elif choice == '3':
                        self.data_export_menu()
                    elif choice == '4':
                        self.database_info()
                    elif choice == '5':
                        self.spatial_data_analysis()
                    elif choice == '6':
                        self.performance_monitoring()
                    else:
                        print("❌ 잘못된 메뉴 번호입니다.")
                
                except KeyboardInterrupt:
                    print("\n\n👋 프로그램을 종료합니다.")
                    break
                except Exception as e:
                    print(f"❌ 오류 발생: {e}")
                    
                input("\nEnter를 눌러 계속...")
        
        finally:
            self.disconnect()

def main():
    """메인 함수"""
    analyzer = PostgreSQLComprehensiveAnalyzer()
    analyzer.run()

if __name__ == "__main__":
    main()
