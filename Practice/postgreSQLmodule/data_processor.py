#!/usr/bin/env python3
"""
Data Processor Module
데이터 처리, 변환, 정리를 위한 모듈
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
import logging
from datetime import datetime
import json


class DataProcessor:
    """데이터 처리 및 변환 클래스"""
    
    def __init__(self):
        """데이터 프로세서 초기화"""
        self.logger = logging.getLogger(__name__)
    
    def clean_data(self, df: pd.DataFrame, 
                   drop_duplicates: bool = True,
                   fill_na_method: str = 'drop',
                   fill_value: Any = None) -> pd.DataFrame:
        """
        데이터 정리
        
        Args:
            df: 입력 DataFrame
            drop_duplicates: 중복 제거 여부
            fill_na_method: NA 처리 방법 ('drop', 'fill', 'forward', 'backward')
            fill_value: fill 방법 사용시 채울 값
            
        Returns:
            정리된 DataFrame
        """
        cleaned_df = df.copy()
        
        # 중복 제거
        if drop_duplicates:
            initial_rows = len(cleaned_df)
            cleaned_df = cleaned_df.drop_duplicates()
            removed_rows = initial_rows - len(cleaned_df)
            if removed_rows > 0:
                self.logger.info(f"중복 행 {removed_rows}개 제거됨")
        
        # NA 값 처리
        if fill_na_method == 'drop':
            initial_rows = len(cleaned_df)
            cleaned_df = cleaned_df.dropna()
            removed_rows = initial_rows - len(cleaned_df)
            if removed_rows > 0:
                self.logger.info(f"NA 포함 행 {removed_rows}개 제거됨")
        elif fill_na_method == 'fill':
            cleaned_df = cleaned_df.fillna(fill_value)
        elif fill_na_method == 'forward':
            cleaned_df = cleaned_df.fillna(method='ffill')
        elif fill_na_method == 'backward':
            cleaned_df = cleaned_df.fillna(method='bfill')
        
        return cleaned_df
    
    def standardize_columns(self, df: pd.DataFrame, 
                          lowercase: bool = True,
                          remove_spaces: bool = True,
                          snake_case: bool = True) -> pd.DataFrame:
        """
        컬럼명 표준화
        
        Args:
            df: 입력 DataFrame
            lowercase: 소문자 변환
            remove_spaces: 공백 제거
            snake_case: 스네이크 케이스 변환
            
        Returns:
            컬럼명이 표준화된 DataFrame
        """
        new_df = df.copy()
        columns = list(new_df.columns)
        
        for i, col in enumerate(columns):
            new_col = str(col)
            
            if lowercase:
                new_col = new_col.lower()
            
            if remove_spaces:
                new_col = new_col.strip()
            
            if snake_case:
                # 공백을 언더스코어로 변경
                new_col = new_col.replace(' ', '_')
                # 특수문자 제거
                import re
                new_col = re.sub(r'[^\w\s]', '', new_col)
                new_col = re.sub(r'\s+', '_', new_col)
            
            columns[i] = new_col
        
        new_df.columns = columns
        return new_df
    
    def convert_data_types(self, df: pd.DataFrame, 
                          type_mapping: Dict[str, str]) -> pd.DataFrame:
        """
        데이터 타입 변환
        
        Args:
            df: 입력 DataFrame
            type_mapping: 컬럼명과 변환할 타입의 매핑
            
        Returns:
            타입이 변환된 DataFrame
        """
        new_df = df.copy()
        
        for column, dtype in type_mapping.items():
            if column in new_df.columns:
                try:
                    if dtype == 'datetime':
                        new_df[column] = pd.to_datetime(new_df[column])
                    elif dtype == 'category':
                        new_df[column] = new_df[column].astype('category')
                    else:
                        new_df[column] = new_df[column].astype(dtype)
                    
                    self.logger.info(f"컬럼 '{column}' 타입을 {dtype}로 변환")
                    
                except Exception as e:
                    self.logger.warning(f"컬럼 '{column}' 타입 변환 실패: {e}")
        
        return new_df
    
    def filter_data(self, df: pd.DataFrame, 
                   filters: Dict[str, Any]) -> pd.DataFrame:
        """
        데이터 필터링
        
        Args:
            df: 입력 DataFrame
            filters: 필터 조건 딕셔너리
            
        Returns:
            필터링된 DataFrame
        """
        filtered_df = df.copy()
        
        for column, condition in filters.items():
            if column not in filtered_df.columns:
                self.logger.warning(f"컬럼 '{column}'이 존재하지 않습니다.")
                continue
            
            if isinstance(condition, dict):
                # 범위 조건
                if 'min' in condition:
                    filtered_df = filtered_df[filtered_df[column] >= condition['min']]
                if 'max' in condition:
                    filtered_df = filtered_df[filtered_df[column] <= condition['max']]
                if 'in' in condition:
                    filtered_df = filtered_df[filtered_df[column].isin(condition['in'])]
                if 'not_in' in condition:
                    filtered_df = filtered_df[~filtered_df[column].isin(condition['not_in'])]
            elif isinstance(condition, (list, tuple)):
                # 리스트 조건 - isin 사용
                filtered_df = filtered_df[filtered_df[column].isin(condition)]
            else:
                # 단순 조건
                filtered_df = filtered_df[filtered_df[column] == condition]
        
        self.logger.info(f"필터링 후 {len(filtered_df)}행 남음")
        return filtered_df
    
    def aggregate_data(self, df: pd.DataFrame,
                      group_by: Union[str, List[str]],
                      aggregations: Dict[str, Union[str, List[str]]]) -> pd.DataFrame:
        """
        데이터 집계
        
        Args:
            df: 입력 DataFrame
            group_by: 그룹핑할 컬럼
            aggregations: 집계 함수 딕셔너리
            
        Returns:
            집계된 DataFrame
        """
        try:
            grouped = df.groupby(group_by)
            result = grouped.agg(aggregations)
            
            # 컬럼명 평면화
            if isinstance(result.columns, pd.MultiIndex):
                result.columns = ['_'.join(col).strip() for col in result.columns.values]
            
            result = result.reset_index()
            self.logger.info(f"데이터 집계 완료: {len(result)}행")
            return result
            
        except Exception as e:
            self.logger.error(f"데이터 집계 실패: {e}")
            return pd.DataFrame()
    
    def pivot_data(self, df: pd.DataFrame,
                   index: Union[str, List[str]],
                   columns: str,
                   values: str,
                   aggfunc: str = 'sum') -> pd.DataFrame:
        """
        데이터 피벗
        
        Args:
            df: 입력 DataFrame
            index: 인덱스로 사용할 컬럼
            columns: 컬럼으로 사용할 컬럼
            values: 값으로 사용할 컬럼
            aggfunc: 집계 함수
            
        Returns:
            피벗된 DataFrame
        """
        try:
            pivot_df = df.pivot_table(
                index=index,
                columns=columns,
                values=values,
                aggfunc=aggfunc,
                fill_value=0
            )
            
            # 컬럼명 정리
            pivot_df.columns.name = None
            pivot_df = pivot_df.reset_index()
            
            self.logger.info(f"피벗 완료: {pivot_df.shape}")
            return pivot_df
            
        except Exception as e:
            self.logger.error(f"피벗 실패: {e}")
            return pd.DataFrame()
    
    def merge_datasets(self, left_df: pd.DataFrame,
                      right_df: pd.DataFrame,
                      on: Union[str, List[str]],
                      how: str = 'inner') -> pd.DataFrame:
        """
        데이터셋 병합
        
        Args:
            left_df: 왼쪽 DataFrame
            right_df: 오른쪽 DataFrame
            on: 조인 키
            how: 조인 방법
            
        Returns:
            병합된 DataFrame
        """
        try:
            merged_df = pd.merge(left_df, right_df, on=on, how=how)
            self.logger.info(f"데이터 병합 완료: {merged_df.shape}")
            return merged_df
            
        except Exception as e:
            self.logger.error(f"데이터 병합 실패: {e}")
            return pd.DataFrame()
    
    def detect_outliers(self, df: pd.DataFrame,
                       columns: List[str],
                       method: str = 'iqr',
                       threshold: float = 1.5) -> pd.DataFrame:
        """
        이상치 탐지
        
        Args:
            df: 입력 DataFrame
            columns: 검사할 컬럼 리스트
            method: 탐지 방법 ('iqr', 'zscore')
            threshold: 임계값
            
        Returns:
            이상치 정보가 포함된 DataFrame
        """
        outlier_df = df.copy()
        outlier_columns = []
        
        for column in columns:
            if column not in df.columns:
                continue
            
            if method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outlier_col = f'{column}_outlier'
                outlier_df[outlier_col] = (
                    (df[column] < lower_bound) | (df[column] > upper_bound)
                )
                outlier_columns.append(outlier_col)
                
            elif method == 'zscore':
                from scipy import stats
                z_scores = np.abs(stats.zscore(df[column]))
                outlier_col = f'{column}_outlier'
                outlier_df[outlier_col] = z_scores > threshold
                outlier_columns.append(outlier_col)
        
        # 전체 이상치 표시
        if outlier_columns:
            outlier_df['is_outlier'] = outlier_df[outlier_columns].any(axis=1)
        
        return outlier_df
    
    def create_time_features(self, df: pd.DataFrame,
                           datetime_column: str) -> pd.DataFrame:
        """
        시간 특성 생성
        
        Args:
            df: 입력 DataFrame
            datetime_column: 날짜/시간 컬럼명
            
        Returns:
            시간 특성이 추가된 DataFrame
        """
        new_df = df.copy()
        
        if datetime_column not in new_df.columns:
            self.logger.error(f"컬럼 '{datetime_column}'이 존재하지 않습니다.")
            return new_df
        
        # 날짜/시간을 datetime으로 변환
        new_df[datetime_column] = pd.to_datetime(new_df[datetime_column])
        dt = new_df[datetime_column]
        
        # 시간 특성 생성
        new_df[f'{datetime_column}_year'] = dt.dt.year
        new_df[f'{datetime_column}_month'] = dt.dt.month
        new_df[f'{datetime_column}_day'] = dt.dt.day
        new_df[f'{datetime_column}_hour'] = dt.dt.hour
        new_df[f'{datetime_column}_minute'] = dt.dt.minute
        new_df[f'{datetime_column}_weekday'] = dt.dt.weekday
        new_df[f'{datetime_column}_quarter'] = dt.dt.quarter
        new_df[f'{datetime_column}_week'] = dt.dt.isocalendar().week
        
        self.logger.info("시간 특성 생성 완료")
        return new_df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        데이터 요약 정보 생성
        
        Args:
            df: 입력 DataFrame
            
        Returns:
            데이터 요약 정보 딕셔너리
        """
        summary = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'numeric_summary': {},
            'categorical_summary': {}
        }
        
        # 수치형 컬럼 요약
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            summary['numeric_summary'] = df[numeric_columns].describe().to_dict()
        
        # 범주형 컬럼 요약
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_columns:
            summary['categorical_summary'][col] = {
                'unique_count': df[col].nunique(),
                'top_values': df[col].value_counts().head(5).to_dict()
            }
        
        return summary
    
    def standardize_data(self, df: pd.DataFrame, 
                        columns: List[str] = None,
                        method: str = 'zscore') -> pd.DataFrame:
        """
        데이터 표준화/정규화
        
        Args:
            df: 입력 DataFrame
            columns: 표준화할 컬럼 리스트 (None이면 모든 수치형 컬럼)
            method: 표준화 방법 ('zscore' 또는 'minmax')
            
        Returns:
            표준화된 DataFrame
        """
        from sklearn.preprocessing import StandardScaler, MinMaxScaler
        
        new_df = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 존재하는 컬럼만 필터링
        valid_columns = [col for col in columns if col in df.columns]
        
        if not valid_columns:
            self.logger.warning("표준화할 수치형 컬럼이 없습니다")
            return new_df
        
        try:
            if method == 'zscore':
                scaler = StandardScaler()
            elif method == 'minmax':
                scaler = MinMaxScaler()
            else:
                raise ValueError(f"지원하지 않는 표준화 방법: {method}")
            
            new_df[valid_columns] = scaler.fit_transform(new_df[valid_columns])
            self.logger.info(f"{method} 방법으로 {len(valid_columns)}개 컬럼 표준화 완료")
            
        except Exception as e:
            self.logger.error(f"데이터 표준화 실패: {e}")
            
        return new_df
