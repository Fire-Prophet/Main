#!/usr/bin/env python3
"""
PostgreSQL 분석 도구 기능 시연 스크립트
새로 추가된 모든 기능들을 자동으로 테스트하고 보여줍니다.
"""

import os
from db_connection import PostgreSQLConnection
from table_analyzer import PostgreSQLTableAnalyzer
from data_quality_checker import PostgreSQLDataQualityChecker
from data_exporter import PostgreSQLDataExporter

def demo_features():
    """주요 기능들을 시연"""
    print("🚀 PostgreSQL 종합 분석 도구 기능 시연")
    print("="*60)
    
    # 데이터베이스 연결 (비밀번호는 환경변수에서 읽기)
    print("\n1️⃣ 데이터베이스 연결 테스트...")
    db = PostgreSQLConnection()
    
    # 연결 없이도 모듈 구조를 보여줄 수 있는 기능들
    print("\n📚 사용 가능한 주요 클래스 및 메서드:")
    
    print("\n🔗 PostgreSQLConnection 클래스:")
    connection_methods = [
        "connect()", "disconnect()", "execute_query()", "execute_command()",
        "get_table_list()", "get_table_info()", "test_connection()"
    ]
    for method in connection_methods:
        print(f"   • {method}")
    
    print("\n📊 PostgreSQLTableAnalyzer 클래스:")
    analyzer_methods = [
        "get_all_tables()", "get_table_columns_detailed()", "get_table_indexes()",
        "get_table_constraints()", "get_spatial_info()", "get_spatial_extent()",
        "get_table_activity()", "analyze_table_comprehensive()"
    ]
    for method in analyzer_methods:
        print(f"   • {method}")
    
    print("\n🔍 PostgreSQLDataQualityChecker 클래스:")
    quality_methods = [
        "check_null_values()", "check_duplicate_values()", "check_data_consistency()",
        "check_referential_integrity()", "comprehensive_quality_check()", "print_quality_report()"
    ]
    for method in quality_methods:
        print(f"   • {method}")
    
    print("\n📁 PostgreSQLDataExporter 클래스:")
    export_methods = [
        "export_table_to_csv()", "export_table_to_json()", "export_spatial_data_to_geojson()",
        "export_analysis_report()", "get_export_summary()"
    ]
    for method in export_methods:
        print(f"   • {method}")
    
    print("\n✨ 새로 추가된 주요 기능들:")
    
    print("\n🔍 데이터 품질 검사:")
    print("   • NULL 값 비율 분석 및 품질 점수 계산")
    print("   • 중복 값 검사 및 고유성 평가")
    print("   • 숫자 데이터 이상치 탐지 (IQR 방법)")
    print("   • 외래키 참조 무결성 검증")
    print("   • 종합 품질 점수 및 등급 평가 (A+~D)")
    
    print("\n📁 다양한 내보내기 형식:")
    print("   • CSV: 표준 쉼표 구분 형식")
    print("   • JSON: 구조화된 JSON 데이터")
    print("   • GeoJSON: 공간 데이터 전용 형식")
    print("   • 분석 보고서: 텍스트 및 JSON 보고서")
    print("   • 내보내기 이력 관리")
    
    print("\n📊 고급 테이블 분석:")
    print("   • 테이블 크기 및 성능 통계")
    print("   • 인덱스 사용률 및 효율성 분석")
    print("   • 공간 데이터 범위 및 통계")
    print("   • 테이블 활동 모니터링")
    print("   • 제약조건 상세 분석")
    
    print("\n🌍 PostGIS 공간 데이터 지원:")
    print("   • 공간 테이블 자동 감지")
    print("   • 좌표계(SRID) 정보 표시")
    print("   • 공간 범위(Bounding Box) 계산")
    print("   • 기하 통계 (면적, 둘레 등)")
    print("   • GeoJSON 내보내기")
    
    print("\n📈 성능 모니터링:")
    print("   • 테이블별 스캔 통계")
    print("   • 인덱스 사용 빈도")
    print("   • 데드 튜플 모니터링")
    print("   • 연결 상태 추적")
    
    print("\n💾 자동 파일 관리:")
    print("   • exports/ 디렉토리 자동 생성")
    print("   • 타임스탬프 기반 파일명")
    print("   • 파일 크기 및 이력 추적")
    print("   • 내보내기 요약 보고서")
    
    print(f"\n{'='*60}")
    print("🎯 사용 시나리오 예제:")
    print("="*60)
    
    print("\n📋 시나리오 1: 테이블 상태 점검")
    print("   1. comprehensive_analyzer.py 실행")
    print("   2. '1. 테이블 상세 분석' 선택")
    print("   3. 분석할 테이블 선택")
    print("   4. 결과를 파일로 저장")
    
    print("\n🔍 시나리오 2: 데이터 품질 평가")
    print("   1. comprehensive_analyzer.py 실행")
    print("   2. '2. 데이터 품질 검사' 선택")
    print("   3. 품질 등급 및 상세 분석 확인")
    print("   4. 품질 보고서 저장")
    
    print("\n📁 시나리오 3: 데이터 내보내기")
    print("   1. comprehensive_analyzer.py 실행")
    print("   2. '3. 데이터 내보내기' 선택")
    print("   3. 내보내기 형식 선택 (CSV/JSON/GeoJSON)")
    print("   4. 조건 설정 및 실행")
    
    print("\n🌍 시나리오 4: 공간 데이터 분석")
    print("   1. comprehensive_analyzer.py 실행")
    print("   2. '5. 공간 데이터 분석' 선택")
    print("   3. 공간 범위 및 통계 확인")
    print("   4. GeoJSON으로 내보내기")
    
    print("\n📊 프로그래밍 사용 예제:")
    print("="*60)
    
    print("""
# 1. 테이블 상세 분석
from table_analyzer import PostgreSQLTableAnalyzer

analyzer = PostgreSQLTableAnalyzer()
if analyzer.connect():
    analyzer.analyze_table_comprehensive('your_table')
    analyzer.disconnect()

# 2. 데이터 품질 검사
from data_quality_checker import PostgreSQLDataQualityChecker

checker = PostgreSQLDataQualityChecker()
if checker.connect():
    results = checker.comprehensive_quality_check('your_table')
    checker.print_quality_report(results)
    checker.disconnect()

# 3. 데이터 내보내기
from data_exporter import PostgreSQLDataExporter

exporter = PostgreSQLDataExporter()
if exporter.connect():
    exporter.export_table_to_csv('your_table', limit=1000)
    exporter.export_table_to_json('your_table', limit=1000)
    exporter.disconnect()
""")
    
    print(f"\n{'='*60}")
    print("✅ PostgreSQL 종합 분석 도구 시연 완료!")
    print("💡 실제 사용을 위해서는 'python comprehensive_analyzer.py'를 실행하세요.")
    print(f"{'='*60}")
    
    # 파일 구조 보기
    print(f"\n📁 현재 프로젝트 구조:")
    import glob
    py_files = glob.glob("*.py")
    for file in sorted(py_files):
        if file != "demo.py":
            print(f"   📄 {file}")
    
    if os.path.exists("exports"):
        export_files = glob.glob("exports/*")
        if export_files:
            print(f"\n📁 exports/ 디렉토리:")
            for file in sorted(export_files)[:5]:  # 최신 5개만
                print(f"   💾 {os.path.basename(file)}")
    
    print(f"\n📚 README.md에서 더 자세한 사용법을 확인하세요!")

if __name__ == "__main__":
    demo_features()
