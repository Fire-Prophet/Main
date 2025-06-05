#!/usr/bin/env python3
"""
PostgreSQL Module - Usage Examples
모듈 사용법 예제 모음
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .database import PostgreSQLManager
from .data_processor import DataProcessor
from .analyzer import DataAnalyzer
from .exporter import DataExporter
from .integration import PostgreSQLIntegrator
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)


def example_1_basic_database_operations():
    """예제 1: 기본 데이터베이스 작업"""
    print("=" * 50)
    print("예제 1: 기본 데이터베이스 작업")
    print("=" * 50)
    
    # 데이터베이스 연결
    db = PostgreSQLManager()
    
    if not db.connect():
        print("데이터베이스 연결 실패")
        return
    
    try:
        # 테이블 목록 조회
        tables = db.get_tables()
        print(f"테이블 목록 ({len(tables)}개):")
        for table in tables[:5]:  # 처음 5개만 표시
            print(f"  - {table}")
        
        if tables:
            # 첫 번째 테이블 정보
            table_name = tables[0]
            print(f"\n'{table_name}' 테이블 정보:")
            
            # 컬럼 정보
            columns = db.get_table_info(table_name)
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']}")
            
            # 행 개수
            row_count = db.get_row_count(table_name)
            print(f"\n행 개수: {row_count:,}")
            
            # 테이블 크기
            size_info = db.get_table_size(table_name)
            if size_info:
                print(f"테이블 크기: {size_info.get('total_size', 'Unknown')}")
    
    finally:
        db.disconnect()


def example_2_data_processing():
    """예제 2: 데이터 처리"""
    print("\n" + "=" * 50)
    print("예제 2: 데이터 처리")
    print("=" * 50)
    
    # 샘플 데이터 생성
    import pandas as pd
    import numpy as np
    
    # 테스트 데이터 생성
    np.random.seed(42)
    data = {
        'ID': range(1, 101),
        'Name': [f'User_{i}' for i in range(1, 101)],
        'Age': np.random.randint(18, 80, 100),
        'Salary': np.random.normal(50000, 15000, 100),
        'Department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], 100),
        'Join Date': pd.date_range('2020-01-01', periods=100, freq='D')
    }
    
    # 일부 결측값 추가
    data['Salary'][::10] = np.nan
    
    df = pd.DataFrame(data)
    print(f"원본 데이터: {df.shape}")
    print(df.head())
    
    # 데이터 프로세서 사용
    processor = DataProcessor()
    
    # 데이터 정리
    cleaned_df = processor.clean_data(df, fill_na_method='fill', fill_value=df['Salary'].mean())
    print(f"\n정리된 데이터: {cleaned_df.shape}")
    
    # 컬럼명 표준화
    standardized_df = processor.standardize_columns(cleaned_df)
    print(f"표준화된 컬럼명: {list(standardized_df.columns)}")
    
    # 데이터 타입 변환
    type_mapping = {'age': 'int32', 'join_date': 'datetime'}
    typed_df = processor.convert_data_types(standardized_df, type_mapping)
    print(f"\n변환된 데이터 타입:")
    print(typed_df.dtypes)
    
    # 필터링
    filters = {
        'age': {'min': 25, 'max': 60},
        'department': {'in': ['IT', 'Finance']}
    }
    filtered_df = processor.filter_data(typed_df, filters)
    print(f"\n필터링된 데이터: {filtered_df.shape}")
    
    # 집계
    aggregations = {
        'salary': ['mean', 'median', 'std'],
        'age': ['min', 'max']
    }
    aggregated_df = processor.aggregate_data(filtered_df, 'department', aggregations)
    print(f"\n집계 결과:")
    print(aggregated_df)


def example_3_data_analysis():
    """예제 3: 데이터 분석"""
    print("\n" + "=" * 50)
    print("예제 3: 데이터 분석")
    print("=" * 50)
    
    # 샘플 데이터 사용 (예제 2와 동일)
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    data = {
        'age': np.random.randint(18, 80, 100),
        'salary': np.random.normal(50000, 15000, 100),
        'experience': np.random.randint(0, 20, 100),
        'department': np.random.choice(['IT', 'HR', 'Finance'], 100),
        'performance': np.random.uniform(1, 5, 100)
    }
    
    df = pd.DataFrame(data)
    
    # 데이터 분석기 사용
    analyzer = DataAnalyzer()
    
    # 기술통계
    desc_stats = analyzer.descriptive_statistics(df)
    print("기술통계 결과:")
    for col, stats in desc_stats.items():
        print(f"\n{col}:")
        print(f"  평균: {stats['mean']:.2f}")
        print(f"  표준편차: {stats['std']:.2f}")
        print(f"  최솟값: {stats['min']:.2f}")
        print(f"  최댓값: {stats['max']:.2f}")
    
    # 상관관계 분석
    corr_analysis = analyzer.correlation_analysis(df)
    print(f"\n강한 상관관계 ({len(corr_analysis['strong_correlations'])}개):")
    for corr in corr_analysis['strong_correlations']:
        print(f"  {corr['variable1']} - {corr['variable2']}: {corr['correlation']:.3f}")
    
    # 범주형 분석
    cat_analysis = analyzer.categorical_analysis(df)
    print(f"\n범주형 변수 분석:")
    for col, analysis in cat_analysis.items():
        print(f"\n{col}:")
        print(f"  고유값 수: {analysis['unique_count']}")
        print(f"  최빈값: {analysis['most_frequent']}")
        print(f"  빈도 분포: {analysis['frequency_distribution']}")
    
    # 인사이트 생성
    insights = analyzer.generate_insights(df)
    print(f"\n데이터 인사이트:")
    for insight in insights:
        print(f"  - {insight}")


def example_4_data_export():
    """예제 4: 데이터 내보내기"""
    print("\n" + "=" * 50)
    print("예제 4: 데이터 내보내기")
    print("=" * 50)
    
    # 샘플 데이터 생성
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    df = pd.DataFrame({
        'product_id': range(1, 51),
        'product_name': [f'Product_{i}' for i in range(1, 51)],
        'price': np.random.uniform(10, 1000, 50),
        'category': np.random.choice(['Electronics', 'Clothing', 'Books'], 50),
        'stock': np.random.randint(0, 100, 50)
    })
    
    # 내보내기 클래스 사용
    exporter = DataExporter("example_exports")
    
    # 여러 형식으로 내보내기
    export_results = exporter.export_multiple_formats(
        df, 
        "sample_products", 
        ['csv', 'json', 'html']
    )
    
    print("내보내기 결과:")
    for format_name, file_path in export_results.items():
        if file_path:
            print(f"  {format_name.upper()}: {file_path}")
        else:
            print(f"  {format_name.upper()}: 실패")
    
    # 데이터 사전 생성
    descriptions = {
        'product_id': '제품 고유 식별자',
        'product_name': '제품명',
        'price': '제품 가격 (USD)',
        'category': '제품 카테고리',
        'stock': '재고 수량'
    }
    
    dict_file = exporter.create_data_dictionary(df, descriptions, "product_dictionary")
    print(f"\n데이터 사전: {dict_file}")
    
    # 내보내기 요약
    summary = exporter.get_export_summary()
    print(f"\n내보내기 요약:")
    print(f"  총 파일 수: {summary['total_files']}")
    print(f"  총 크기: {summary['total_size_mb']:.2f} MB")
    print(f"  파일 형식: {summary['file_types']}")


def example_5_integrated_workflow():
    """예제 5: 통합 워크플로우"""
    print("\n" + "=" * 50)
    print("예제 5: 통합 워크플로우 (데이터베이스 연결 필요)")
    print("=" * 50)
    
    try:
        # 통합 클래스 사용
        integrator = PostgreSQLIntegrator()
        
        if not integrator.connect():
            print("데이터베이스 연결 실패 - 통합 예제를 건너뜁니다.")
            return
        
        try:
            # 데이터베이스 개요
            overview = integrator.get_database_overview()
            print(f"데이터베이스 개요:")
            print(f"  총 테이블 수: {overview['summary']['total_tables']}")
            print(f"  총 행 수: {overview['summary']['total_rows']:,}")
            print(f"  가장 큰 테이블: {overview['summary']['largest_table']}")
            
            # 테이블이 있는 경우 분석 수행
            if overview['summary']['total_tables'] > 0:
                table_name = list(overview['tables'].keys())[0]
                print(f"\n'{table_name}' 테이블 분석 중...")
                
                # 테이블 분석 (작은 샘플만)
                analysis_result = integrator.custom_analysis(
                    f'SELECT * FROM "{table_name}" LIMIT 100',
                    f"{table_name}_sample",
                    export_results=True
                )
                
                if 'analysis' in analysis_result and 'insights' in analysis_result['analysis']:
                    print("\n주요 인사이트:")
                    for insight in analysis_result['analysis']['insights']:
                        print(f"  - {insight}")
                
                if 'export_files' in analysis_result:
                    print(f"\n결과 파일:")
                    for file_type, file_path in analysis_result['export_files'].items():
                        print(f"  {file_type}: {file_path}")
            
        finally:
            integrator.disconnect()
            
    except Exception as e:
        print(f"통합 예제 실행 중 오류: {e}")


def main():
    """모든 예제 실행"""
    print("PostgreSQL Module 사용 예제")
    print("=" * 50)
    
    try:
        # 기본 예제들 (데이터베이스 연결 없이 실행 가능)
        example_2_data_processing()
        example_3_data_analysis()
        example_4_data_export()
        
        # 데이터베이스 관련 예제들
        example_1_basic_database_operations()
        example_5_integrated_workflow()
        
    except Exception as e:
        print(f"예제 실행 중 오류 발생: {e}")
    
    print("\n" + "=" * 50)
    print("모든 예제 실행 완료!")
    print("=" * 50)


if __name__ == "__main__":
    main()
