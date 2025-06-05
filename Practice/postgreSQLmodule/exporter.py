#!/usr/bin/env python3
"""
Data Exporter Module
다양한 형식으로 데이터 내보내기를 위한 모듈
"""

import json
import csv
import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import logging
from pathlib import Path


class DataExporter:
    """데이터 내보내기 클래스"""
    
    def __init__(self, export_dir: str = "exports"):
        """
        데이터 내보내기 초기화
        
        Args:
            export_dir: 내보내기 디렉토리
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def to_csv(self, data: Union[pd.DataFrame, List[Dict]], 
               filename: str,
               index: bool = False,
               encoding: str = 'utf-8-sig') -> str:
        """
        CSV 파일로 내보내기
        
        Args:
            data: 내보낼 데이터 (DataFrame 또는 딕셔너리 리스트)
            filename: 파일명
            index: 인덱스 포함 여부
            encoding: 인코딩
            
        Returns:
            저장된 파일 경로
        """
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = self.export_dir / filename
        
        try:
            if isinstance(data, pd.DataFrame):
                data.to_csv(filepath, index=index, encoding=encoding)
            elif isinstance(data, list) and data:
                df = pd.DataFrame(data)
                df.to_csv(filepath, index=index, encoding=encoding)
            else:
                raise ValueError("지원하지 않는 데이터 형식입니다.")
            
            self.logger.info(f"CSV 파일 저장 완료: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"CSV 저장 실패: {e}")
            return ""
    
    def to_excel(self, data: Union[pd.DataFrame, Dict[str, pd.DataFrame]], 
                 filename: str,
                 index: bool = False) -> str:
        """
        Excel 파일로 내보내기
        
        Args:
            data: 내보낼 데이터 (DataFrame 또는 시트별 DataFrame 딕셔너리)
            filename: 파일명
            index: 인덱스 포함 여부
            
        Returns:
            저장된 파일 경로
        """
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        filepath = self.export_dir / filename
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                if isinstance(data, pd.DataFrame):
                    data.to_excel(writer, sheet_name='Sheet1', index=index)
                elif isinstance(data, dict):
                    for sheet_name, df in data.items():
                        if isinstance(df, pd.DataFrame):
                            df.to_excel(writer, sheet_name=sheet_name, index=index)
                else:
                    raise ValueError("지원하지 않는 데이터 형식입니다.")
            
            self.logger.info(f"Excel 파일 저장 완료: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Excel 저장 실패: {e}")
            return ""
    
    def to_json(self, data: Union[Dict, List, pd.DataFrame], 
                filename: str,
                indent: int = 2,
                ensure_ascii: bool = False) -> str:
        """
        JSON 파일로 내보내기
        
        Args:
            data: 내보낼 데이터
            filename: 파일명
            indent: 들여쓰기
            ensure_ascii: ASCII 인코딩 강제 여부
            
        Returns:
            저장된 파일 경로
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.export_dir / filename
        
        try:
            # DataFrame을 딕셔너리로 변환
            if isinstance(data, pd.DataFrame):
                export_data = data.to_dict('records')
            else:
                export_data = data
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=indent, ensure_ascii=ensure_ascii, 
                         default=self._json_serializer)
            
            self.logger.info(f"JSON 파일 저장 완료: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"JSON 저장 실패: {e}")
            return ""
    
    def to_parquet(self, data: pd.DataFrame, filename: str) -> str:
        """
        Parquet 파일로 내보내기
        
        Args:
            data: 내보낼 DataFrame
            filename: 파일명
            
        Returns:
            저장된 파일 경로
        """
        if not filename.endswith('.parquet'):
            filename += '.parquet'
        
        filepath = self.export_dir / filename
        
        try:
            data.to_parquet(filepath, index=False)
            self.logger.info(f"Parquet 파일 저장 완료: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Parquet 저장 실패: {e}")
            return ""
    
    def to_html(self, data: pd.DataFrame, 
                filename: str,
                title: str = "Data Report",
                include_summary: bool = True) -> str:
        """
        HTML 리포트로 내보내기
        
        Args:
            data: 내보낼 DataFrame
            filename: 파일명
            title: 리포트 제목
            include_summary: 요약 정보 포함 여부
            
        Returns:
            저장된 파일 경로
        """
        if not filename.endswith('.html'):
            filename += '.html'
        
        filepath = self.export_dir / filename
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title}</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    h2 {{ color: #666; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .summary {{ background-color: #f9f9f9; padding: 15px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <h1>{title}</h1>
                <p>생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            """
            
            if include_summary:
                html_content += f"""
                <div class="summary">
                    <h2>데이터 요약</h2>
                    <p>행 수: {len(data):,}</p>
                    <p>열 수: {len(data.columns)}</p>
                    <p>데이터 타입:</p>
                    <ul>
                """
                
                for dtype, count in data.dtypes.value_counts().items():
                    html_content += f"<li>{dtype}: {count}개</li>"
                
                html_content += """
                    </ul>
                </div>
                """
            
            # 데이터 테이블 추가
            html_content += "<h2>데이터</h2>"
            html_content += data.to_html(escape=False, table_id="data-table")
            
            html_content += """
            </body>
            </html>
            """
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML 리포트 저장 완료: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"HTML 저장 실패: {e}")
            return ""
    
    def create_analysis_report(self, analysis_results: Dict[str, Any],
                             filename: str = None) -> str:
        """
        분석 결과 리포트 생성
        
        Args:
            analysis_results: 분석 결과 딕셔너리
            filename: 파일명
            
        Returns:
            저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_report_{timestamp}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'data_analysis',
                'version': '1.0'
            },
            'analysis_results': analysis_results
        }
        
        return self.to_json(report, filename)
    
    def create_data_dictionary(self, df: pd.DataFrame, 
                             descriptions: Optional[Dict[str, str]] = None,
                             filename: str = None) -> str:
        """
        데이터 사전 생성
        
        Args:
            df: 분석할 DataFrame
            descriptions: 컬럼 설명 딕셔너리
            filename: 파일명
            
        Returns:
            저장된 파일 경로
        """
        if filename is None:
            filename = "data_dictionary.csv"
        
        # 데이터 사전 생성
        data_dict = []
        
        for col in df.columns:
            col_info = {
                'column_name': col,
                'data_type': str(df[col].dtype),
                'non_null_count': df[col].count(),
                'null_count': df[col].isnull().sum(),
                'null_percentage': round((df[col].isnull().sum() / len(df)) * 100, 2),
                'unique_count': df[col].nunique(),
                'description': descriptions.get(col, '') if descriptions else ''
            }
            
            # 수치형 컬럼의 경우 추가 정보
            if df[col].dtype in ['int64', 'float64']:
                col_info.update({
                    'min_value': df[col].min(),
                    'max_value': df[col].max(),
                    'mean': round(df[col].mean(), 2) if not df[col].isnull().all() else None,
                    'median': df[col].median()
                })
            
            # 범주형 컬럼의 경우 최빈값
            elif df[col].dtype == 'object':
                mode_value = df[col].mode()
                col_info['most_frequent'] = mode_value.iloc[0] if len(mode_value) > 0 else None
            
            data_dict.append(col_info)
        
        return self.to_csv(data_dict, filename)
    
    def export_multiple_formats(self, data: pd.DataFrame,
                              base_filename: str,
                              formats: List[str] = ['csv', 'excel', 'json']) -> Dict[str, str]:
        """
        여러 형식으로 동시 내보내기
        
        Args:
            data: 내보낼 DataFrame
            base_filename: 기본 파일명
            formats: 내보낼 형식 리스트
            
        Returns:
            형식별 저장 경로 딕셔너리
        """
        results = {}
        
        for fmt in formats:
            try:
                if fmt == 'csv':
                    results['csv'] = self.to_csv(data, base_filename)
                elif fmt == 'excel':
                    results['excel'] = self.to_excel(data, base_filename)
                elif fmt == 'json':
                    results['json'] = self.to_json(data, base_filename)
                elif fmt == 'parquet':
                    results['parquet'] = self.to_parquet(data, base_filename)
                elif fmt == 'html':
                    results['html'] = self.to_html(data, base_filename)
                
            except Exception as e:
                self.logger.error(f"{fmt} 형식 내보내기 실패: {e}")
                results[fmt] = ""
        
        return results
    
    def create_summary_report(self, data: pd.DataFrame,
                            analysis_results: Optional[Dict] = None,
                            filename: str = None) -> str:
        """
        종합 요약 리포트 생성
        
        Args:
            data: 원본 DataFrame
            analysis_results: 분석 결과
            filename: 파일명
            
        Returns:
            저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_report_{timestamp}.html"
        
        return self.to_html(data, filename, "데이터 분석 요약 리포트", True)
    
    def _json_serializer(self, obj):
        """JSON 직렬화를 위한 헬퍼 함수"""
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return str(obj)
    
    def get_export_summary(self) -> Dict[str, Any]:
        """
        내보내기 요약 정보 반환
        
        Returns:
            내보내기 디렉토리 정보
        """
        files = list(self.export_dir.glob('*'))
        
        summary = {
            'export_directory': str(self.export_dir),
            'total_files': len(files),
            'file_types': {},
            'total_size_mb': 0
        }
        
        for file_path in files:
            if file_path.is_file():
                ext = file_path.suffix.lower()
                summary['file_types'][ext] = summary['file_types'].get(ext, 0) + 1
                summary['total_size_mb'] += file_path.stat().st_size / (1024 * 1024)
        
        summary['total_size_mb'] = round(summary['total_size_mb'], 2)
        
        return summary
