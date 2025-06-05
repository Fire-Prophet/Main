#!/usr/bin/env python3
"""
PostgreSQL 데이터 품질 검사 모듈
데이터 무결성, 일관성, 완전성 등을 검사하는 기능 제공
"""

from db_connection import PostgreSQLConnection
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class PostgreSQLDataQualityChecker:
    """PostgreSQL 데이터 품질 검사 클래스"""
    
    def __init__(self):
        self.db = PostgreSQLConnection()
    
    def connect(self):
        """데이터베이스 연결"""
        return self.db.connect()
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        self.db.disconnect()
    
    def check_null_values(self, table_name: str) -> Dict[str, Any]:
        """NULL 값 검사"""
        try:
            # 테이블의 모든 컬럼 정보 조회
            columns_query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
            """
            columns = self.db.execute_query(columns_query, (table_name,))
            
            if not columns:
                return {'error': 'Table not found or no columns'}
            
            null_analysis = []
            
            for col in columns:
                col_name = col['column_name']
                
                # NULL 값 개수 조회
                null_count_query = f"""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT("{col_name}") as non_null_count,
                    COUNT(*) - COUNT("{col_name}") as null_count,
                    ROUND(
                        (COUNT(*) - COUNT("{col_name}")) * 100.0 / NULLIF(COUNT(*), 0), 2
                    ) as null_percentage
                FROM "{table_name}"
                """
                
                result = self.db.execute_query(null_count_query)
                
                if result:
                    row = result[0]
                    null_analysis.append({
                        'column_name': col_name,
                        'data_type': col['data_type'],
                        'is_nullable': col['is_nullable'],
                        'total_rows': row['total_rows'],
                        'null_count': row['null_count'],
                        'null_percentage': float(row['null_percentage'] or 0),
                        'quality_score': 100 - float(row['null_percentage'] or 0)
                    })
            
            return {
                'table_name': table_name,
                'analysis_type': 'null_values',
                'columns': null_analysis,
                'summary': {
                    'total_columns': len(null_analysis),
                    'columns_with_nulls': len([c for c in null_analysis if c['null_count'] > 0]),
                    'avg_quality_score': round(sum(c['quality_score'] for c in null_analysis) / len(null_analysis), 2) if null_analysis else 0
                }
            }
            
        except Exception as e:
            return {'error': f'NULL 값 검사 실패: {e}'}
    
    def check_duplicate_values(self, table_name: str, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """중복 값 검사"""
        try:
            if not columns:
                # 모든 컬럼에 대해 중복 검사
                columns_query = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position
                """
                column_results = self.db.execute_query(columns_query, (table_name,))
                columns = [col['column_name'] for col in column_results]
            
            duplicate_analysis = []
            
            for col_name in columns:
                # 중복 값 검사
                dup_query = f"""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT "{col_name}") as unique_values,
                    COUNT(*) - COUNT(DISTINCT "{col_name}") as duplicate_count,
                    ROUND(
                        (COUNT(*) - COUNT(DISTINCT "{col_name}")) * 100.0 / NULLIF(COUNT(*), 0), 2
                    ) as duplicate_percentage
                FROM "{table_name}"
                WHERE "{col_name}" IS NOT NULL
                """
                
                result = self.db.execute_query(dup_query)
                
                if result:
                    row = result[0]
                    
                    # 가장 빈번한 중복값 조회
                    frequent_query = f"""
                    SELECT "{col_name}" as value, COUNT(*) as frequency
                    FROM "{table_name}"
                    WHERE "{col_name}" IS NOT NULL
                    GROUP BY "{col_name}"
                    HAVING COUNT(*) > 1
                    ORDER BY COUNT(*) DESC
                    LIMIT 5
                    """
                    
                    frequent_dups = self.db.execute_query(frequent_query)
                    
                    duplicate_analysis.append({
                        'column_name': col_name,
                        'total_rows': row['total_rows'],
                        'unique_values': row['unique_values'],
                        'duplicate_count': row['duplicate_count'],
                        'duplicate_percentage': float(row['duplicate_percentage'] or 0),
                        'uniqueness_score': round(100 - float(row['duplicate_percentage'] or 0), 2),
                        'most_frequent_duplicates': frequent_dups[:5] if frequent_dups else []
                    })
            
            return {
                'table_name': table_name,
                'analysis_type': 'duplicate_values',
                'columns': duplicate_analysis,
                'summary': {
                    'total_columns_checked': len(duplicate_analysis),
                    'columns_with_duplicates': len([c for c in duplicate_analysis if c['duplicate_count'] > 0]),
                    'avg_uniqueness_score': round(sum(c['uniqueness_score'] for c in duplicate_analysis) / len(duplicate_analysis), 2) if duplicate_analysis else 0
                }
            }
            
        except Exception as e:
            return {'error': f'중복 값 검사 실패: {e}'}
    
    def check_data_consistency(self, table_name: str) -> Dict[str, Any]:
        """데이터 일관성 검사"""
        try:
            consistency_checks = []
            
            # 숫자 컬럼의 이상치 검사
            numeric_columns_query = """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
                AND data_type IN ('integer', 'bigint', 'decimal', 'numeric', 'real', 'double precision')
            """
            
            numeric_columns = self.db.execute_query(numeric_columns_query, (table_name,))
            
            for col in numeric_columns:
                col_name = col['column_name']
                
                # 기본 통계 조회
                stats_query = f"""
                SELECT 
                    COUNT(*) as total_count,
                    COUNT("{col_name}") as non_null_count,
                    MIN("{col_name}") as min_value,
                    MAX("{col_name}") as max_value,
                    AVG("{col_name}") as avg_value,
                    STDDEV("{col_name}") as std_dev,
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "{col_name}") as q1,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "{col_name}") as median,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "{col_name}") as q3
                FROM "{table_name}"
                WHERE "{col_name}" IS NOT NULL
                """
                
                stats = self.db.execute_query(stats_query)
                
                if stats and stats[0]['non_null_count'] > 0:
                    stat = stats[0]
                    
                    # IQR을 이용한 이상치 검사
                    if stat['q1'] is not None and stat['q3'] is not None:
                        iqr = float(stat['q3']) - float(stat['q1'])
                        lower_bound = float(stat['q1']) - 1.5 * iqr
                        upper_bound = float(stat['q3']) + 1.5 * iqr
                        
                        outlier_query = f"""
                        SELECT COUNT(*) as outlier_count
                        FROM "{table_name}"
                        WHERE "{col_name}" IS NOT NULL
                            AND ("{col_name}" < {lower_bound} OR "{col_name}" > {upper_bound})
                        """
                        
                        outlier_result = self.db.execute_query(outlier_query)
                        outlier_count = outlier_result[0]['outlier_count'] if outlier_result else 0
                        outlier_percentage = round(outlier_count * 100.0 / stat['non_null_count'], 2)
                        
                        consistency_checks.append({
                            'column_name': col_name,
                            'data_type': col['data_type'],
                            'total_values': stat['non_null_count'],
                            'min_value': float(stat['min_value']) if stat['min_value'] is not None else None,
                            'max_value': float(stat['max_value']) if stat['max_value'] is not None else None,
                            'avg_value': round(float(stat['avg_value']), 2) if stat['avg_value'] is not None else None,
                            'std_dev': round(float(stat['std_dev']), 2) if stat['std_dev'] is not None else None,
                            'q1': float(stat['q1']) if stat['q1'] is not None else None,
                            'median': float(stat['median']) if stat['median'] is not None else None,
                            'q3': float(stat['q3']) if stat['q3'] is not None else None,
                            'outlier_count': outlier_count,
                            'outlier_percentage': outlier_percentage,
                            'consistency_score': max(0, round(100 - outlier_percentage, 2))
                        })
            
            return {
                'table_name': table_name,
                'analysis_type': 'data_consistency',
                'numeric_columns': consistency_checks,
                'summary': {
                    'total_numeric_columns': len(consistency_checks),
                    'columns_with_outliers': len([c for c in consistency_checks if c['outlier_count'] > 0]),
                    'avg_consistency_score': round(sum(c['consistency_score'] for c in consistency_checks) / len(consistency_checks), 2) if consistency_checks else 0
                }
            }
            
        except Exception as e:
            return {'error': f'데이터 일관성 검사 실패: {e}'}
    
    def check_referential_integrity(self, table_name: str) -> Dict[str, Any]:
        """참조 무결성 검사"""
        try:
            # 외래키 제약조건 조회
            fk_query = """
            SELECT 
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = %s
            """
            
            foreign_keys = self.db.execute_query(fk_query, (table_name,))
            
            integrity_checks = []
            
            for fk in foreign_keys:
                # 참조 무결성 위반 검사
                violation_query = f"""
                SELECT COUNT(*) as violation_count
                FROM "{table_name}" t
                LEFT JOIN "{fk['foreign_table_name']}" ft 
                    ON t."{fk['column_name']}" = ft."{fk['foreign_column_name']}"
                WHERE t."{fk['column_name']}" IS NOT NULL
                    AND ft."{fk['foreign_column_name']}" IS NULL
                """
                
                violation_result = self.db.execute_query(violation_query)
                violation_count = violation_result[0]['violation_count'] if violation_result else 0
                
                # 총 레코드 수 조회
                total_query = f"""
                SELECT COUNT(*) as total_count
                FROM "{table_name}"
                WHERE "{fk['column_name']}" IS NOT NULL
                """
                
                total_result = self.db.execute_query(total_query)
                total_count = total_result[0]['total_count'] if total_result else 0
                
                violation_percentage = round(violation_count * 100.0 / total_count, 2) if total_count > 0 else 0
                
                integrity_checks.append({
                    'constraint_name': fk['constraint_name'],
                    'column_name': fk['column_name'],
                    'foreign_table': fk['foreign_table_name'],
                    'foreign_column': fk['foreign_column_name'],
                    'total_references': total_count,
                    'violation_count': violation_count,
                    'violation_percentage': violation_percentage,
                    'integrity_score': round(100 - violation_percentage, 2)
                })
            
            return {
                'table_name': table_name,
                'analysis_type': 'referential_integrity',
                'foreign_keys': integrity_checks,
                'summary': {
                    'total_foreign_keys': len(integrity_checks),
                    'keys_with_violations': len([c for c in integrity_checks if c['violation_count'] > 0]),
                    'avg_integrity_score': round(sum(c['integrity_score'] for c in integrity_checks) / len(integrity_checks), 2) if integrity_checks else 100
                }
            }
            
        except Exception as e:
            return {'error': f'참조 무결성 검사 실패: {e}'}
    
    def comprehensive_quality_check(self, table_name: str) -> Dict[str, Any]:
        """종합 데이터 품질 검사"""
        try:
            print(f"\n🔍 테이블 '{table_name}' 데이터 품질 종합 검사 시작...")
            
            results = {
                'table_name': table_name,
                'analysis_date': datetime.now().isoformat(),
                'checks': {}
            }
            
            # 1. NULL 값 검사
            print("   📋 NULL 값 검사 중...")
            null_check = self.check_null_values(table_name)
            results['checks']['null_values'] = null_check
            
            # 2. 중복 값 검사
            print("   🔄 중복 값 검사 중...")
            dup_check = self.check_duplicate_values(table_name)
            results['checks']['duplicate_values'] = dup_check
            
            # 3. 데이터 일관성 검사
            print("   📊 데이터 일관성 검사 중...")
            consistency_check = self.check_data_consistency(table_name)
            results['checks']['data_consistency'] = consistency_check
            
            # 4. 참조 무결성 검사
            print("   🔗 참조 무결성 검사 중...")
            integrity_check = self.check_referential_integrity(table_name)
            results['checks']['referential_integrity'] = integrity_check
            
            # 종합 점수 계산
            scores = []
            if 'summary' in null_check:
                scores.append(null_check['summary'].get('avg_quality_score', 0))
            if 'summary' in dup_check:
                scores.append(dup_check['summary'].get('avg_uniqueness_score', 0))
            if 'summary' in consistency_check:
                scores.append(consistency_check['summary'].get('avg_consistency_score', 0))
            if 'summary' in integrity_check:
                scores.append(integrity_check['summary'].get('avg_integrity_score', 0))
            
            overall_score = round(sum(scores) / len(scores), 2) if scores else 0
            
            results['overall_quality_score'] = overall_score
            results['quality_grade'] = self._get_quality_grade(overall_score)
            
            return results
            
        except Exception as e:
            return {'error': f'종합 데이터 품질 검사 실패: {e}'}
    
    def _get_quality_grade(self, score: float) -> str:
        """품질 점수를 등급으로 변환"""
        if score >= 95:
            return "A+ (최우수)"
        elif score >= 90:
            return "A (우수)"
        elif score >= 85:
            return "B+ (양호)"
        elif score >= 80:
            return "B (보통)"
        elif score >= 70:
            return "C (개선 필요)"
        else:
            return "D (대폭 개선 필요)"
    
    def print_quality_report(self, quality_results: Dict[str, Any]):
        """품질 검사 결과를 보기 좋게 출력"""
        if 'error' in quality_results:
            print(f"❌ {quality_results['error']}")
            return
        
        print(f"\n{'='*60}")
        print(f"📊 데이터 품질 검사 보고서")
        print(f"{'='*60}")
        print(f"테이블: {quality_results.get('table_name', 'N/A')}")
        print(f"검사일시: {quality_results.get('analysis_date', 'N/A')}")
        print(f"종합 점수: {quality_results.get('overall_quality_score', 0)}/100")
        print(f"품질 등급: {quality_results.get('quality_grade', 'N/A')}")
        print(f"{'='*60}")
        
        checks = quality_results.get('checks', {})
        
        # NULL 값 검사 결과
        if 'null_values' in checks and 'summary' in checks['null_values']:
            null_summary = checks['null_values']['summary']
            print(f"\n🔍 NULL 값 검사:")
            print(f"   • 검사 컬럼 수: {null_summary.get('total_columns', 0)}")
            print(f"   • NULL 포함 컬럼: {null_summary.get('columns_with_nulls', 0)}")
            print(f"   • 평균 품질 점수: {null_summary.get('avg_quality_score', 0)}/100")
        
        # 중복 값 검사 결과
        if 'duplicate_values' in checks and 'summary' in checks['duplicate_values']:
            dup_summary = checks['duplicate_values']['summary']
            print(f"\n🔄 중복 값 검사:")
            print(f"   • 검사 컬럼 수: {dup_summary.get('total_columns_checked', 0)}")
            print(f"   • 중복 포함 컬럼: {dup_summary.get('columns_with_duplicates', 0)}")
            print(f"   • 평균 고유성 점수: {dup_summary.get('avg_uniqueness_score', 0)}/100")
        
        # 데이터 일관성 검사 결과
        if 'data_consistency' in checks and 'summary' in checks['data_consistency']:
            consistency_summary = checks['data_consistency']['summary']
            print(f"\n📊 데이터 일관성 검사:")
            print(f"   • 숫자 컬럼 수: {consistency_summary.get('total_numeric_columns', 0)}")
            print(f"   • 이상치 포함 컬럼: {consistency_summary.get('columns_with_outliers', 0)}")
            print(f"   • 평균 일관성 점수: {consistency_summary.get('avg_consistency_score', 0)}/100")
        
        # 참조 무결성 검사 결과
        if 'referential_integrity' in checks and 'summary' in checks['referential_integrity']:
            integrity_summary = checks['referential_integrity']['summary']
            print(f"\n🔗 참조 무결성 검사:")
            print(f"   • 외래키 수: {integrity_summary.get('total_foreign_keys', 0)}")
            print(f"   • 위반 발견 키: {integrity_summary.get('keys_with_violations', 0)}")
            print(f"   • 평균 무결성 점수: {integrity_summary.get('avg_integrity_score', 0)}/100")

def main():
    """테스트 및 예제 함수"""
    checker = PostgreSQLDataQualityChecker()
    
    if not checker.connect():
        print("❌ 데이터베이스 연결 실패!")
        return
    
    try:
        # 사용 가능한 테이블 조회
        tables_query = """
        SELECT tablename, pg_size_pretty(pg_total_relation_size(quote_ident(tablename))) as size
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(quote_ident(tablename)) DESC
        LIMIT 5
        """
        
        tables = checker.db.execute_query(tables_query)
        
        if tables:
            print("📋 데이터 품질 검사 가능한 테이블 (상위 5개):")
            for i, table in enumerate(tables, 1):
                print(f"   {i}. {table['tablename']} ({table['size']})")
                
            print("\n💡 사용법:")
            print("   from data_quality_checker import PostgreSQLDataQualityChecker")
            print("   checker = PostgreSQLDataQualityChecker()")
            print("   checker.connect()")
            print("   results = checker.comprehensive_quality_check('테이블명')")
            print("   checker.print_quality_report(results)")
    
    finally:
        checker.disconnect()

if __name__ == "__main__":
    main()
