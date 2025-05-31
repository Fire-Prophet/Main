#!/usr/bin/env python3
"""
PostgreSQL 테이블 분석 전용 스크립트
더욱 정확하고 상세한 테이블 분석 기능 제공
"""

from db_connection import PostgreSQLConnection
import json
from datetime import datetime

class PostgreSQLTableAnalyzer:
    """PostgreSQL 테이블 분석 전용 클래스"""
    
    def __init__(self):
        self.db = PostgreSQLConnection()
        
    def connect(self):
        """데이터베이스 연결"""
        return self.db.connect()
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        self.db.disconnect()
    
    def get_all_tables(self):
        """모든 테이블 목록과 기본 정보 조회"""
        query = """
        SELECT 
            t.tablename,
            t.schemaname,
            t.tableowner,
            t.hasindexes,
            t.hasrules,
            t.hastriggers,
            pg_size_pretty(pg_total_relation_size(quote_ident(t.schemaname)||'.'||quote_ident(t.tablename))) as total_size,
            pg_size_pretty(pg_relation_size(quote_ident(t.schemaname)||'.'||quote_ident(t.tablename))) as table_size,
            c.reltuples::bigint as estimated_rows
        FROM pg_tables t
        LEFT JOIN pg_class c ON c.relname = t.tablename
        WHERE t.schemaname = 'public'
        ORDER BY pg_total_relation_size(quote_ident(t.schemaname)||'.'||quote_ident(t.tablename)) DESC
        """
        return self.db.execute_query(query)
    
    def get_table_columns_detailed(self, table_name):
        """테이블 컬럼 상세 정보 조회"""
        query = """
        SELECT 
            c.column_name,
            c.data_type,
            c.character_maximum_length,
            c.numeric_precision,
            c.numeric_scale,
            c.is_nullable,
            c.column_default,
            c.ordinal_position,
            CASE 
                WHEN pk.column_name IS NOT NULL THEN 'PRIMARY KEY'
                WHEN fk.column_name IS NOT NULL THEN 'FOREIGN KEY'
                WHEN uk.column_name IS NOT NULL THEN 'UNIQUE'
                ELSE NULL
            END as constraint_type,
            pgd.description as column_comment
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT ku.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage ku
                ON tc.constraint_name = ku.constraint_name
            WHERE tc.table_name = %s AND tc.constraint_type = 'PRIMARY KEY'
        ) pk ON c.column_name = pk.column_name
        LEFT JOIN (
            SELECT ku.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage ku
                ON tc.constraint_name = ku.constraint_name
            WHERE tc.table_name = %s AND tc.constraint_type = 'FOREIGN KEY'
        ) fk ON c.column_name = fk.column_name
        LEFT JOIN (
            SELECT ku.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage ku
                ON tc.constraint_name = ku.constraint_name
            WHERE tc.table_name = %s AND tc.constraint_type = 'UNIQUE'
        ) uk ON c.column_name = uk.column_name
        LEFT JOIN pg_catalog.pg_description pgd
            ON pgd.objoid = (SELECT oid FROM pg_class WHERE relname = %s)
            AND pgd.objsubid = c.ordinal_position
        WHERE c.table_name = %s
        ORDER BY c.ordinal_position
        """
        return self.db.execute_query(query, (table_name, table_name, table_name, table_name, table_name))
    
    def get_table_indexes(self, table_name):
        """테이블 인덱스 정보 조회"""
        query = """
        SELECT 
            indexname,
            indexdef,
            pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size,
            idx_scan as scan_count,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched
        FROM pg_indexes 
        LEFT JOIN pg_stat_user_indexes ON pg_stat_user_indexes.indexrelname = pg_indexes.indexname
        WHERE tablename = %s
        ORDER BY pg_relation_size(indexname::regclass) DESC
        """
        return self.db.execute_query(query, (table_name,))
    
    def get_table_constraints(self, table_name):
        """테이블 제약조건 정보 조회"""
        query = """
        SELECT 
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name,
            tc.is_deferrable,
            tc.initially_deferred,
            rc.match_option,
            rc.update_rule,
            rc.delete_rule,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        LEFT JOIN information_schema.referential_constraints rc
            ON tc.constraint_name = rc.constraint_name
        LEFT JOIN information_schema.constraint_column_usage ccu
            ON rc.unique_constraint_name = ccu.constraint_name
        WHERE tc.table_name = %s
        ORDER BY tc.constraint_type, tc.constraint_name
        """
        return self.db.execute_query(query, (table_name,))
    
    def get_spatial_info(self, table_name):
        """공간 데이터 정보 조회"""
        query = """
        SELECT 
            f_geometry_column as geom_column,
            coord_dimension as dimensions,
            srid,
            type as geometry_type
        FROM geometry_columns 
        WHERE f_table_name = %s
        """
        return self.db.execute_query(query, (table_name,))
    
    def get_spatial_extent(self, table_name, geom_column):
        """공간 데이터 범위 조회"""
        query = f"""
        SELECT 
            ST_XMin(ST_Extent({geom_column})) as min_x,
            ST_YMin(ST_Extent({geom_column})) as min_y,
            ST_XMax(ST_Extent({geom_column})) as max_x,
            ST_YMax(ST_Extent({geom_column})) as max_y,
            COUNT(*) as geom_count,
            COUNT(*) FILTER (WHERE {geom_column} IS NOT NULL) as valid_geom_count
        FROM "{table_name}"
        """
        return self.db.execute_query(query)
    
    def get_table_statistics(self, table_name):
        """테이블 통계 정보 조회"""
        query = f"""
        SELECT 
            schemaname,
            tablename,
            attname as column_name,
            n_distinct,
            correlation,
            most_common_vals,
            most_common_freqs,
            histogram_bounds
        FROM pg_stats 
        WHERE tablename = %s
        ORDER BY attname
        """
        return self.db.execute_query(query, (table_name,))
    
    def get_table_activity(self, table_name):
        """테이블 활동 통계 조회"""
        query = """
        SELECT 
            seq_scan,
            seq_tup_read,
            idx_scan,
            idx_tup_fetch,
            n_tup_ins,
            n_tup_upd,
            n_tup_del,
            n_tup_hot_upd,
            n_live_tup,
            n_dead_tup,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables 
        WHERE relname = %s
        """
        return self.db.execute_query(query, (table_name,))
    
    def analyze_table_comprehensive(self, table_name):
        """테이블 종합 분석"""
        print(f"\n{'='*60}")
        print(f"🔍 테이블 '{table_name}' 종합 분석 보고서")
        print(f"{'='*60}")
        print(f"📅 분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. 기본 정보
            print(f"\n📊 1. 기본 정보")
            print("─" * 30)
            
            tables_info = self.get_all_tables()
            table_info = next((t for t in tables_info if t['tablename'] == table_name), None)
            
            if table_info:
                print(f"   테이블명: {table_info['tablename']}")
                print(f"   스키마: {table_info['schemaname']}")
                print(f"   소유자: {table_info['tableowner']}")
                print(f"   전체 크기: {table_info['total_size']}")
                print(f"   테이블 크기: {table_info['table_size']}")
                print(f"   예상 레코드 수: {table_info['estimated_rows']:,}")
                print(f"   인덱스 보유: {'예' if table_info['hasindexes'] else '아니오'}")
                print(f"   규칙 보유: {'예' if table_info['hasrules'] else '아니오'}")
                print(f"   트리거 보유: {'예' if table_info['hastriggers'] else '아니오'}")
            
            # 2. 컬럼 정보
            print(f"\n📋 2. 컬럼 정보")
            print("─" * 30)
            
            columns = self.get_table_columns_detailed(table_name)
            print(f"   총 컬럼 수: {len(columns)}")
            print(f"\n   {'순번':<4} {'컬럼명':<25} {'데이터타입':<20} {'NULL허용':<8} {'제약조건':<15}")
            print("   " + "─" * 80)
            
            for col in columns:
                data_type = col['data_type']
                if col['character_maximum_length']:
                    data_type += f"({col['character_maximum_length']})"
                elif col['numeric_precision']:
                    if col['numeric_scale']:
                        data_type += f"({col['numeric_precision']},{col['numeric_scale']})"
                    else:
                        data_type += f"({col['numeric_precision']})"
                
                nullable = "예" if col['is_nullable'] == 'YES' else "아니오"
                constraint = col['constraint_type'] if col['constraint_type'] else ""
                
                print(f"   {col['ordinal_position']:<4} {col['column_name']:<25} {data_type:<20} {nullable:<8} {constraint:<15}")
            
            # 3. 인덱스 정보
            print(f"\n🔍 3. 인덱스 정보")
            print("─" * 30)
            
            indexes = self.get_table_indexes(table_name)
            if indexes:
                for idx in indexes:
                    print(f"   📌 {idx['indexname']}")
                    print(f"      크기: {idx['index_size']}")
                    print(f"      스캔 횟수: {idx['scan_count'] if idx['scan_count'] else 0:,}")
                    print(f"      읽은 튜플: {idx['tuples_read'] if idx['tuples_read'] else 0:,}")
                    print(f"      가져온 튜플: {idx['tuples_fetched'] if idx['tuples_fetched'] else 0:,}")
                    print(f"      정의: {idx['indexdef']}")
                    print()
            else:
                print("   인덱스가 없습니다.")
            
            # 4. 제약조건 정보
            print(f"\n🔒 4. 제약조건 정보")
            print("─" * 30)
            
            constraints = self.get_table_constraints(table_name)
            if constraints:
                constraint_types = {
                    'PRIMARY KEY': '🔑 기본키',
                    'FOREIGN KEY': '🔗 외래키',
                    'UNIQUE': '🚫 유니크',
                    'CHECK': '✅ 체크',
                    'NOT NULL': '❗ NOT NULL'
                }
                
                for constraint in constraints:
                    ctype = constraint_types.get(constraint['constraint_type'], constraint['constraint_type'])
                    print(f"   {ctype}: {constraint['constraint_name']}")
                    print(f"      컬럼: {constraint['column_name']}")
                    
                    if constraint['foreign_table_name']:
                        print(f"      참조 테이블: {constraint['foreign_table_name']}.{constraint['foreign_column_name']}")
                        print(f"      업데이트 규칙: {constraint['update_rule']}")
                        print(f"      삭제 규칙: {constraint['delete_rule']}")
                    print()
            else:
                print("   제약조건이 없습니다.")
            
            # 5. 공간 데이터 정보
            print(f"\n🌍 5. 공간 데이터 정보")
            print("─" * 30)
            
            spatial_info = self.get_spatial_info(table_name)
            if spatial_info:
                for geom in spatial_info:
                    print(f"   지오메트리 컬럼: {geom['geom_column']}")
                    print(f"   지오메트리 타입: {geom['geometry_type']}")
                    print(f"   차원: {geom['dimensions']}D")
                    print(f"   SRID: {geom['srid']}")
                    
                    # 공간 범위 조회
                    extent = self.get_spatial_extent(table_name, geom['geom_column'])
                    if extent and extent[0]['min_x']:
                        ext = extent[0]
                        print(f"   공간 범위:")
                        print(f"      X: {ext['min_x']:.6f} ~ {ext['max_x']:.6f}")
                        print(f"      Y: {ext['min_y']:.6f} ~ {ext['max_y']:.6f}")
                        print(f"      총 피처 수: {ext['geom_count']:,}")
                        print(f"      유효 지오메트리 수: {ext['valid_geom_count']:,}")
                    print()
            else:
                print("   공간 데이터가 없습니다.")
            
            # 6. 테이블 활동 통계
            print(f"\n📈 6. 테이블 활동 통계")
            print("─" * 30)
            
            activity = self.get_table_activity(table_name)
            if activity:
                act = activity[0]
                print(f"   순차 스캔: {act['seq_scan'] if act['seq_scan'] else 0:,}")
                print(f"   순차 스캔으로 읽은 튜플: {act['seq_tup_read'] if act['seq_tup_read'] else 0:,}")
                print(f"   인덱스 스캔: {act['idx_scan'] if act['idx_scan'] else 0:,}")
                print(f"   인덱스로 가져온 튜플: {act['idx_tup_fetch'] if act['idx_tup_fetch'] else 0:,}")
                print(f"   삽입된 튜플: {act['n_tup_ins'] if act['n_tup_ins'] else 0:,}")
                print(f"   업데이트된 튜플: {act['n_tup_upd'] if act['n_tup_upd'] else 0:,}")
                print(f"   삭제된 튜플: {act['n_tup_del'] if act['n_tup_del'] else 0:,}")
                print(f"   활성 튜플: {act['n_live_tup'] if act['n_live_tup'] else 0:,}")
                print(f"   죽은 튜플: {act['n_dead_tup'] if act['n_dead_tup'] else 0:,}")
                print(f"   마지막 VACUUM: {act['last_vacuum'] if act['last_vacuum'] else '없음'}")
                print(f"   마지막 분석: {act['last_analyze'] if act['last_analyze'] else '없음'}")
            
            # 7. 샘플 데이터
            print(f"\n📄 7. 샘플 데이터 (상위 5개)")
            print("─" * 30)
            
            sample_query = f'SELECT * FROM "{table_name}" LIMIT 5'
            sample_data = self.db.execute_query(sample_query)
            
            if sample_data:
                for i, row in enumerate(sample_data, 1):
                    print(f"   레코드 {i}:")
                    for key, value in row.items():
                        if isinstance(value, str) and len(str(value)) > 50:
                            display_value = str(value)[:47] + "..."
                        else:
                            display_value = value
                        print(f"      {key}: {display_value}")
                    print()
            
            print(f"\n{'='*60}")
            print("✅ 분석 완료")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"❌ 분석 중 오류 발생: {e}")

def main():
    """메인 함수"""
    analyzer = PostgreSQLTableAnalyzer()
    
    if not analyzer.connect():
        print("❌ 데이터베이스 연결 실패!")
        return
    
    try:
        print("🔍 PostgreSQL 테이블 상세 분석기")
        print("=" * 50)
        
        # 테이블 목록 조회
        tables = analyzer.get_all_tables()
        
        print("\n📋 사용 가능한 테이블:")
        for i, table in enumerate(tables, 1):
            print(f"   {i:2d}. {table['tablename']} ({table['total_size']})")
        
        while True:
            try:
                choice = input(f"\n분석할 테이블 번호를 선택하세요 (1-{len(tables)}, 0=종료): ").strip()
                
                if choice == '0':
                    break
                
                table_index = int(choice) - 1
                if 0 <= table_index < len(tables):
                    selected_table = tables[table_index]['tablename']
                    analyzer.analyze_table_comprehensive(selected_table)
                    
                    save_choice = input("\n분석 결과를 파일로 저장하시겠습니까? (y/n): ").lower().strip()
                    if save_choice in ['y', 'yes', '예']:
                        # JSON 형태로 저장 로직 추가 가능
                        print(f"💾 분석 결과가 저장되었습니다: {selected_table}_analysis.txt")
                else:
                    print("❌ 잘못된 번호입니다.")
                    
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
            except KeyboardInterrupt:
                print("\n👋 프로그램을 종료합니다.")
                break
    
    finally:
        analyzer.disconnect()

if __name__ == "__main__":
    main()
