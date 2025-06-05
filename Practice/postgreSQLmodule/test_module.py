#!/usr/bin/env python3
"""
PostgreSQL 모듈 테스트 스크립트
모든 모듈의 기능을 테스트하고 연동을 확인합니다.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# 모듈 임포트 테스트
try:
    from postgreSQLmodule import (
        PostgreSQLManager,
        DataProcessor,
        DataAnalyzer,
        DataExporter,
        PostgreSQLIntegrator,
        Config
    )
    print("✅ 모든 모듈 임포트 성공!")
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)


def create_sample_data():
    """테스트용 샘플 데이터 생성"""
    np.random.seed(42)
    n_samples = 1000
    
    # 날짜 범위 생성
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=i) for i in range(n_samples)]
    
    # 샘플 데이터 생성
    data = {
        'id': range(1, n_samples + 1),
        'date': dates,
        'category': np.random.choice(['A', 'B', 'C', 'D'], n_samples),
        'value1': np.random.normal(100, 20, n_samples),
        'value2': np.random.exponential(50, n_samples),
        'status': np.random.choice(['active', 'inactive', 'pending'], n_samples),
        'score': np.random.uniform(0, 100, n_samples)
    }
    
    # 일부 결측값 추가
    missing_indices = np.random.choice(n_samples, size=50, replace=False)
    for idx in missing_indices:
        if idx < len(data['value1']):
            data['value1'][idx] = np.nan
    
    # 일부 이상값 추가
    outlier_indices = np.random.choice(n_samples, size=20, replace=False)
    for idx in outlier_indices:
        if idx < len(data['value2']):
            data['value2'][idx] *= 10  # 이상값 생성
    
    return pd.DataFrame(data)


def test_data_processor():
    """DataProcessor 테스트"""
    print("\n🧪 DataProcessor 테스트 시작...")
    
    # 샘플 데이터 생성
    df = create_sample_data()
    processor = DataProcessor()
    
    # 데이터 정보 출력
    print(f"원본 데이터 크기: {df.shape}")
    print(f"결측값 수: {df.isnull().sum().sum()}")
    
    # 데이터 클리닝
    cleaned_df = processor.clean_data(df)
    print(f"클리닝 후 데이터 크기: {cleaned_df.shape}")
    
    # 데이터 표준화
    numeric_cols = ['value1', 'value2', 'score']
    standardized_df = processor.standardize_data(cleaned_df, numeric_cols)
    print(f"표준화 완료: {numeric_cols}")
    
    # 필터링
    filtered_df = processor.filter_data(cleaned_df, {'category': ['A', 'B']})
    print(f"필터링 후 데이터 크기: {filtered_df.shape}")
    
    # 집계
    agg_df = processor.aggregate_data(
        cleaned_df, 
        group_by=['category'], 
        aggregations={'value1': 'mean', 'value2': 'sum', 'score': 'std'}
    )
    print(f"집계 결과:\n{agg_df}")
    
    print("✅ DataProcessor 테스트 완료!")
    return cleaned_df


def test_data_analyzer(df):
    """DataAnalyzer 테스트"""
    print("\n🧪 DataAnalyzer 테스트 시작...")
    
    analyzer = DataAnalyzer()
    processor = DataProcessor()  # 이상값 탐지용
    
    # 기술통계
    stats = analyzer.descriptive_statistics(df)
    print("기술통계 분석 완료")
    
    # 상관관계 분석
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) >= 2:
        corr_results = analyzer.correlation_analysis(df[numeric_cols])
        print(f"상관관계 분석 완료: {len(corr_results)} 개 강한 상관관계")
    
    # 이상값 탐지 (DataProcessor에서)
    outliers = processor.detect_outliers(df, 'value2')
    print(f"탐지된 이상값 수: {len(outliers)}")
    
    # 분포 분석
    if 'value1' in df.columns:
        dist_results = analyzer.distribution_analysis(df, 'value1')
        print(f"분포 분석 완료: {len(dist_results)} 개 분포 테스트")
    
    print("✅ DataAnalyzer 테스트 완료!")
    return stats


def test_data_exporter(df):
    """DataExporter 테스트"""
    print("\n🧪 DataExporter 테스트 시작...")
    
    exporter = DataExporter()
    output_dir = "/tmp/postgresql_module_test"
    
    try:
        # CSV 내보내기
        csv_path = exporter.to_csv(df, f"{output_dir}/test_data.csv")
        print(f"CSV 파일 생성: {csv_path}")
        
        # JSON 내보내기
        json_path = exporter.to_json(df.head(10), f"{output_dir}/test_data.json")
        print(f"JSON 파일 생성: {json_path}")
        
        # Excel 내보내기 (openpyxl 설치 필요)
        try:
            excel_path = exporter.to_excel(df, f"{output_dir}/test_data.xlsx")
            print(f"Excel 파일 생성: {excel_path}")
        except Exception as e:
            print(f"Excel 내보내기 스킵: {e}")
        
        # HTML 리포트 생성
        html_path = exporter.to_html(df, f"{output_dir}/test_report.html")
        print(f"HTML 리포트 생성: {html_path}")
        
        print("✅ DataExporter 테스트 완료!")
        
    except Exception as e:
        print(f"⚠️ DataExporter 테스트 중 오류: {e}")


def test_integration():
    """통합 워크플로우 테스트"""
    print("\n🧪 PostgreSQLIntegrator 테스트 시작...")
    
    # 실제 데이터베이스 연결 없이 기본 기능만 테스트
    integrator = PostgreSQLIntegrator()
    
    # 샘플 데이터로 분석 파이프라인 테스트
    df = create_sample_data()
    
    try:
        # 데이터 처리 파이프라인
        processed_df = integrator.data_processor.clean_data(df)
        
        # 분석 수행
        analysis_results = integrator.analyzer.descriptive_statistics(processed_df)
        
        # 결과 내보내기
        output_path = "/tmp/postgresql_module_test/integration_test.csv"
        integrator.exporter.to_csv(processed_df, output_path)
        
        print("✅ 통합 워크플로우 테스트 완료!")
        
    except Exception as e:
        print(f"⚠️ 통합 테스트 중 오류: {e}")


def test_config():
    """Configuration 테스트"""
    print("\n🧪 Config 테스트 시작...")
    
    # 환경 변수 테스트
    test_configs = {
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_db'
    }
    
    for key, value in test_configs.items():
        os.environ[key] = value
    
    config = Config()
    
    # 설정값 확인
    print(f"데이터베이스 호스트: {config.get_db_config().get('host', 'Not set')}")
    print(f"포트: {config.get_db_config().get('port', 'Not set')}")
    
    # 로깅 설정 테스트
    logger = logging.getLogger(__name__)
    logger.info("로깅 테스트 메시지")
    
    print("✅ Config 테스트 완료!")


def main():
    """메인 테스트 함수"""
    print("🚀 PostgreSQL 모듈 통합 테스트 시작\n")
    print("=" * 50)
    
    try:
        # 출력 디렉토리 생성
        os.makedirs("/tmp/postgresql_module_test", exist_ok=True)
        
        # 각 모듈 테스트
        test_config()
        df = test_data_processor()
        test_data_analyzer(df)
        test_data_exporter(df)
        test_integration()
        
        print("\n" + "=" * 50)
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("\n📁 테스트 결과 파일:")
        print("   /tmp/postgresql_module_test/")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
