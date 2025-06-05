#!/usr/bin/env python3
"""
PostgreSQL Module - Integration Example
모든 모듈을 통합하여 사용하는 예제
"""

from .database import PostgreSQLManager
from .data_processor import DataProcessor
from .analyzer import DataAnalyzer
from .exporter import DataExporter
import pandas as pd
import logging
from typing import Dict, Any


class PostgreSQLIntegrator:
    """PostgreSQL 모듈 통합 클래스"""
    
    def __init__(self, db_config: Dict[str, Any] = None):
        """
        통합 클래스 초기화
        
        Args:
            db_config: 데이터베이스 설정 딕셔너리
        """
        # 기본 설정
        default_config = {
            'host': '123.212.210.230',
            'port': 5432,
            'user': 'postgres',
            'database': 'gis_db',
            'password': None
        }
        
        if db_config:
            default_config.update(db_config)
        
        # 모듈 초기화
        self.db = PostgreSQLManager(**default_config)
        self.processor = DataProcessor()
        self.analyzer = DataAnalyzer()
        self.exporter = DataExporter()
        
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """데이터베이스 연결"""
        return self.db.connect()
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        self.db.disconnect()
    
    def analyze_table(self, table_name: str,
                     clean_data: bool = True,
                     export_results: bool = True) -> Dict[str, Any]:
        """
        테이블 완전 분석
        
        Args:
            table_name: 분석할 테이블명
            clean_data: 데이터 정리 여부
            export_results: 결과 내보내기 여부
            
        Returns:
            분석 결과 딕셔너리
        """
        self.logger.info(f"테이블 '{table_name}' 분석 시작")
        
        # 1. 데이터 로드
        query = f'SELECT * FROM "{table_name}"'
        df = self.db.to_dataframe(query)
        
        if df.empty:
            self.logger.warning(f"테이블 '{table_name}'이 비어있습니다.")
            return {}
        
        self.logger.info(f"데이터 로드 완료: {df.shape}")
        
        # 2. 데이터 정리 (옵션)
        if clean_data:
            df = self.processor.clean_data(df)
            df = self.processor.standardize_columns(df)
            self.logger.info(f"데이터 정리 완료: {df.shape}")
        
        # 3. 분석 수행
        analysis_results = {}
        
        # 기술통계
        analysis_results['descriptive'] = self.analyzer.descriptive_statistics(df)
        
        # 상관관계 분석
        analysis_results['correlation'] = self.analyzer.correlation_analysis(df)
        
        # 분포 분석
        analysis_results['distribution'] = self.analyzer.distribution_analysis(df)
        
        # 이상치 분석
        analysis_results['outliers'] = self.analyzer.outlier_analysis(df)
        
        # 범주형 분석
        analysis_results['categorical'] = self.analyzer.categorical_analysis(df)
        
        # 인사이트 생성
        insights = self.analyzer.generate_insights(df)
        analysis_results['insights'] = insights
        
        # 데이터 요약
        analysis_results['data_summary'] = self.processor.get_data_summary(df)
        
        # 4. 결과 내보내기 (옵션)
        if export_results:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            
            # 분석 결과 JSON 저장
            report_file = self.exporter.create_analysis_report(
                analysis_results, 
                f"{table_name}_analysis_{timestamp}"
            )
            
            # 데이터 사전 생성
            dict_file = self.exporter.create_data_dictionary(
                df, 
                filename=f"{table_name}_dictionary_{timestamp}.csv"
            )
            
            # 정리된 데이터 저장
            data_file = self.exporter.to_csv(
                df, 
                f"{table_name}_cleaned_{timestamp}.csv"
            )
            
            analysis_results['export_files'] = {
                'report': report_file,
                'dictionary': dict_file,
                'cleaned_data': data_file
            }
        
        self.logger.info(f"테이블 '{table_name}' 분석 완료")
        return analysis_results
    
    def compare_tables(self, table_names: list,
                      join_column: str = None,
                      export_results: bool = True) -> Dict[str, Any]:
        """
        여러 테이블 비교 분석
        
        Args:
            table_names: 비교할 테이블 리스트
            join_column: 조인할 컬럼 (None이면 개별 분석)
            export_results: 결과 내보내기 여부
            
        Returns:
            비교 분석 결과
        """
        self.logger.info(f"{len(table_names)}개 테이블 비교 분석 시작")
        
        results = {
            'tables': {},
            'comparison': {}
        }
        
        dataframes = {}
        
        # 각 테이블 개별 분석
        for table_name in table_names:
            table_result = self.analyze_table(table_name, export_results=False)
            results['tables'][table_name] = table_result
            
            # DataFrame 저장 (비교용)
            query = f'SELECT * FROM "{table_name}"'
            df = self.db.to_dataframe(query)
            dataframes[table_name] = df
        
        # 테이블 간 비교
        if len(dataframes) > 1:
            # 크기 비교
            results['comparison']['sizes'] = {
                name: {'rows': df.shape[0], 'columns': df.shape[1]} 
                for name, df in dataframes.items()
            }
            
            # 공통 컬럼 찾기
            all_columns = [set(df.columns) for df in dataframes.values()]
            common_columns = set.intersection(*all_columns)
            results['comparison']['common_columns'] = list(common_columns)
            
            # 조인 분석 (가능한 경우)
            if join_column and join_column in common_columns:
                try:
                    # 첫 번째 테이블부터 차례로 조인
                    merged_df = dataframes[table_names[0]]
                    for table_name in table_names[1:]:
                        merged_df = self.processor.merge_datasets(
                            merged_df, 
                            dataframes[table_name], 
                            on=join_column, 
                            how='outer'
                        )
                    
                    results['comparison']['merged_analysis'] = {
                        'shape': merged_df.shape,
                        'join_column': join_column,
                        'total_unique_values': merged_df[join_column].nunique()
                    }
                    
                except Exception as e:
                    self.logger.warning(f"테이블 조인 실패: {e}")
        
        # 결과 내보내기
        if export_results:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.exporter.create_analysis_report(
                results, 
                f"table_comparison_{timestamp}"
            )
            results['export_file'] = report_file
        
        self.logger.info("테이블 비교 분석 완료")
        return results
    
    def custom_analysis(self, query: str,
                       analysis_name: str = "custom",
                       export_results: bool = True) -> Dict[str, Any]:
        """
        사용자 정의 쿼리 분석
        
        Args:
            query: 실행할 SQL 쿼리
            analysis_name: 분석 이름
            export_results: 결과 내보내기 여부
            
        Returns:
            분석 결과
        """
        self.logger.info(f"사용자 정의 분석 '{analysis_name}' 시작")
        
        # 쿼리 실행
        df = self.db.to_dataframe(query)
        
        if df.empty:
            self.logger.warning("쿼리 결과가 비어있습니다.")
            return {}
        
        # 데이터 정리
        df = self.processor.clean_data(df)
        df = self.processor.standardize_columns(df)
        
        # 분석 수행
        results = {
            'query': query,
            'data_shape': df.shape,
            'analysis': {}
        }
        
        # 기본 분석
        results['analysis']['descriptive'] = self.analyzer.descriptive_statistics(df)
        results['analysis']['correlation'] = self.analyzer.correlation_analysis(df)
        results['analysis']['categorical'] = self.analyzer.categorical_analysis(df)
        results['analysis']['insights'] = self.analyzer.generate_insights(df)
        
        # 결과 내보내기
        if export_results:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            
            # 분석 결과 저장
            report_file = self.exporter.create_analysis_report(
                results, 
                f"{analysis_name}_analysis_{timestamp}"
            )
            
            # 데이터 저장
            data_file = self.exporter.to_csv(
                df, 
                f"{analysis_name}_data_{timestamp}.csv"
            )
            
            results['export_files'] = {
                'report': report_file,
                'data': data_file
            }
        
        self.logger.info(f"사용자 정의 분석 '{analysis_name}' 완료")
        return results
    
    def get_database_overview(self) -> Dict[str, Any]:
        """
        데이터베이스 전체 개요 생성
        
        Returns:
            데이터베이스 개요 정보
        """
        self.logger.info("데이터베이스 개요 생성 시작")
        
        overview = {
            'connection_info': {
                'host': self.db.host,
                'database': self.db.database,
                'user': self.db.user
            },
            'tables': {}
        }
        
        # 모든 테이블 정보 수집
        table_names = self.db.get_tables()
        
        for table_name in table_names:
            try:
                table_info = self.db.get_table_info(table_name)
                table_size = self.db.get_table_size(table_name)
                row_count = self.db.get_row_count(table_name)
                
                overview['tables'][table_name] = {
                    'columns': len(table_info),
                    'rows': row_count,
                    'size': table_size.get('total_size', 'Unknown'),
                    'column_info': table_info
                }
                
            except Exception as e:
                self.logger.warning(f"테이블 '{table_name}' 정보 수집 실패: {e}")
                overview['tables'][table_name] = {'error': str(e)}
        
        # 전체 통계
        overview['summary'] = {
            'total_tables': len(table_names),
            'total_rows': sum(info.get('rows', 0) for info in overview['tables'].values()),
            'largest_table': max(overview['tables'].items(), 
                               key=lambda x: x[1].get('rows', 0))[0] if table_names else None
        }
        
        self.logger.info("데이터베이스 개요 생성 완료")
        return overview
    
    def __enter__(self):
        """Context manager 진입"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.disconnect()


def main():
    """사용 예제"""
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # 통합 클래스 사용
    with PostgreSQLIntegrator() as integrator:
        # 데이터베이스 개요
        overview = integrator.get_database_overview()
        print("=== 데이터베이스 개요 ===")
        print(f"총 테이블 수: {overview['summary']['total_tables']}")
        print(f"총 행 수: {overview['summary']['total_rows']:,}")
        
        # 첫 번째 테이블 분석 (예제)
        if overview['summary']['total_tables'] > 0:
            table_name = list(overview['tables'].keys())[0]
            print(f"\n=== '{table_name}' 테이블 분석 ===")
            
            analysis_result = integrator.analyze_table(table_name)
            
            if 'insights' in analysis_result:
                print("주요 인사이트:")
                for insight in analysis_result['insights']:
                    print(f"- {insight}")


if __name__ == "__main__":
    main()
