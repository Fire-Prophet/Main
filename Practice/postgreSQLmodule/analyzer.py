#!/usr/bin/env python3
"""
Data Analyzer Module
데이터 분석, 통계, 인사이트 생성을 위한 모듈
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
import logging
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class DataAnalyzer:
    """데이터 분석 클래스"""
    
    def __init__(self):
        """데이터 분석기 초기화"""
        self.logger = logging.getLogger(__name__)
        self.analysis_results = {}
    
    def descriptive_statistics(self, df: pd.DataFrame, 
                             columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        기술통계 분석
        
        Args:
            df: 입력 DataFrame
            columns: 분석할 컬럼 리스트 (None이면 모든 수치형 컬럼)
            
        Returns:
            기술통계 결과 딕셔너리
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        results = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            series = df[col].dropna()
            
            results[col] = {
                'count': len(series),
                'mean': series.mean(),
                'median': series.median(),
                'mode': series.mode().iloc[0] if len(series.mode()) > 0 else None,
                'std': series.std(),
                'var': series.var(),
                'min': series.min(),
                'max': series.max(),
                'range': series.max() - series.min(),
                'q1': series.quantile(0.25),
                'q3': series.quantile(0.75),
                'iqr': series.quantile(0.75) - series.quantile(0.25),
                'skewness': series.skew(),
                'kurtosis': series.kurtosis(),
                'missing_count': df[col].isnull().sum(),
                'missing_percentage': (df[col].isnull().sum() / len(df)) * 100
            }
        
        self.analysis_results['descriptive_stats'] = results
        self.logger.info(f"기술통계 분석 완료: {len(results)}개 컬럼")
        return results
    
    def correlation_analysis(self, df: pd.DataFrame,
                           method: str = 'pearson',
                           threshold: float = 0.5) -> Dict[str, Any]:
        """
        상관관계 분석
        
        Args:
            df: 입력 DataFrame
            method: 상관계수 방법 ('pearson', 'spearman', 'kendall')
            threshold: 강한 상관관계 임계값
            
        Returns:
            상관관계 분석 결과
        """
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            self.logger.warning("수치형 데이터가 없습니다.")
            return {}
        
        # 상관계수 행렬 계산
        corr_matrix = numeric_df.corr(method=method)
        
        # 강한 상관관계 쌍 찾기
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    strong_correlations.append({
                        'variable1': corr_matrix.columns[i],
                        'variable2': corr_matrix.columns[j],
                        'correlation': corr_value,
                        'strength': 'strong' if abs(corr_value) >= 0.7 else 'moderate'
                    })
        
        results = {
            'correlation_matrix': corr_matrix.to_dict(),
            'strong_correlations': strong_correlations,
            'method': method,
            'threshold': threshold
        }
        
        self.analysis_results['correlation'] = results
        self.logger.info(f"상관관계 분석 완료: {len(strong_correlations)}개 강한 상관관계 발견")
        return results
    
    def distribution_analysis(self, df: pd.DataFrame,
                            columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        분포 분석
        
        Args:
            df: 입력 DataFrame
            columns: 분석할 컬럼 리스트
            
        Returns:
            분포 분석 결과
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        results = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            series = df[col].dropna()
            
            # 정규성 검정 (Shapiro-Wilk test)
            if len(series) <= 5000:  # 표본 크기 제한
                try:
                    shapiro_stat, shapiro_p = stats.shapiro(series)
                    is_normal = shapiro_p > 0.05
                except:
                    shapiro_stat, shapiro_p = None, None
                    is_normal = False
            else:
                shapiro_stat, shapiro_p = None, None
                is_normal = False
            
            # 히스토그램 분석
            hist, bins = np.histogram(series, bins=30)
            
            results[col] = {
                'shapiro_statistic': shapiro_stat,
                'shapiro_p_value': shapiro_p,
                'is_normal_distribution': is_normal,
                'unique_values': series.nunique(),
                'histogram_data': {
                    'counts': hist.tolist(),
                    'bins': bins.tolist()
                }
            }
        
        self.analysis_results['distribution'] = results
        self.logger.info(f"분포 분석 완료: {len(results)}개 컬럼")
        return results
    
    def outlier_analysis(self, df: pd.DataFrame,
                        columns: Optional[List[str]] = None,
                        methods: List[str] = ['iqr', 'zscore']) -> Dict[str, Any]:
        """
        이상치 분석
        
        Args:
            df: 입력 DataFrame
            columns: 분석할 컬럼 리스트
            methods: 이상치 탐지 방법
            
        Returns:
            이상치 분석 결과
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        results = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            series = df[col].dropna()
            col_results = {}
            
            # IQR 방법
            if 'iqr' in methods:
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers_iqr = series[(series < lower_bound) | (series > upper_bound)]
                
                col_results['iqr'] = {
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'outlier_count': len(outliers_iqr),
                    'outlier_percentage': (len(outliers_iqr) / len(series)) * 100,
                    'outlier_values': outliers_iqr.tolist()
                }
            
            # Z-Score 방법
            if 'zscore' in methods:
                z_scores = np.abs(stats.zscore(series))
                outliers_zscore = series[z_scores > 3]
                
                col_results['zscore'] = {
                    'threshold': 3,
                    'outlier_count': len(outliers_zscore),
                    'outlier_percentage': (len(outliers_zscore) / len(series)) * 100,
                    'outlier_values': outliers_zscore.tolist()
                }
            
            results[col] = col_results
        
        self.analysis_results['outliers'] = results
        self.logger.info(f"이상치 분석 완료: {len(results)}개 컬럼")
        return results
    
    def time_series_analysis(self, df: pd.DataFrame,
                           datetime_column: str,
                           value_columns: List[str]) -> Dict[str, Any]:
        """
        시계열 분석
        
        Args:
            df: 입력 DataFrame
            datetime_column: 날짜/시간 컬럼
            value_columns: 분석할 값 컬럼들
            
        Returns:
            시계열 분석 결과
        """
        if datetime_column not in df.columns:
            self.logger.error(f"날짜 컬럼 '{datetime_column}'이 존재하지 않습니다.")
            return {}
        
        # 날짜 컬럼을 datetime으로 변환하고 정렬
        ts_df = df.copy()
        ts_df[datetime_column] = pd.to_datetime(ts_df[datetime_column])
        ts_df = ts_df.sort_values(datetime_column)
        
        results = {
            'period': {
                'start_date': ts_df[datetime_column].min(),
                'end_date': ts_df[datetime_column].max(),
                'total_days': (ts_df[datetime_column].max() - ts_df[datetime_column].min()).days
            },
            'trends': {},
            'seasonality': {},
            'statistics': {}
        }
        
        for col in value_columns:
            if col not in ts_df.columns:
                continue
            
            series = ts_df.set_index(datetime_column)[col].dropna()
            
            # 추세 분석
            if len(series) > 1:
                x = np.arange(len(series))
                slope, intercept, r_value, p_value, std_err = stats.linregr(x, series.values)
                
                results['trends'][col] = {
                    'slope': slope,
                    'r_squared': r_value**2,
                    'p_value': p_value,
                    'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
                }
            
            # 월별/주별 패턴 분석
            monthly_stats = series.groupby(series.index.month).agg(['mean', 'std']).to_dict()
            weekly_stats = series.groupby(series.index.dayofweek).agg(['mean', 'std']).to_dict()
            
            results['seasonality'][col] = {
                'monthly_pattern': monthly_stats,
                'weekly_pattern': weekly_stats
            }
            
            # 기본 통계
            results['statistics'][col] = {
                'mean': series.mean(),
                'std': series.std(),
                'min': series.min(),
                'max': series.max(),
                'volatility': series.std() / series.mean() if series.mean() != 0 else 0
            }
        
        self.analysis_results['time_series'] = results
        self.logger.info(f"시계열 분석 완료: {len(value_columns)}개 변수")
        return results
    
    def categorical_analysis(self, df: pd.DataFrame,
                           columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        범주형 변수 분석
        
        Args:
            df: 입력 DataFrame
            columns: 분석할 컬럼 리스트
            
        Returns:
            범주형 분석 결과
        """
        if columns is None:
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        results = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            series = df[col].dropna()
            value_counts = series.value_counts()
            
            results[col] = {
                'unique_count': series.nunique(),
                'most_frequent': value_counts.index[0] if len(value_counts) > 0 else None,
                'most_frequent_count': value_counts.iloc[0] if len(value_counts) > 0 else 0,
                'least_frequent': value_counts.index[-1] if len(value_counts) > 0 else None,
                'least_frequent_count': value_counts.iloc[-1] if len(value_counts) > 0 else 0,
                'frequency_distribution': value_counts.to_dict(),
                'missing_count': df[col].isnull().sum(),
                'missing_percentage': (df[col].isnull().sum() / len(df)) * 100,
                'entropy': stats.entropy(value_counts.values)  # 정보 엔트로피
            }
        
        self.analysis_results['categorical'] = results
        self.logger.info(f"범주형 분석 완료: {len(results)}개 컬럼")
        return results
    
    def hypothesis_testing(self, df: pd.DataFrame,
                          group_column: str,
                          value_column: str,
                          test_type: str = 'auto') -> Dict[str, Any]:
        """
        가설 검정
        
        Args:
            df: 입력 DataFrame
            group_column: 그룹 변수
            value_column: 값 변수
            test_type: 검정 방법 ('auto', 'ttest', 'anova', 'kruskal')
            
        Returns:
            가설 검정 결과
        """
        if group_column not in df.columns or value_column not in df.columns:
            self.logger.error("지정된 컬럼이 존재하지 않습니다.")
            return {}
        
        # 그룹별 데이터 분리
        groups = df.groupby(group_column)[value_column].apply(list).to_dict()
        group_names = list(groups.keys())
        group_data = [np.array(groups[name]) for name in group_names]
        
        # 그룹이 2개인 경우
        if len(group_data) == 2:
            if test_type in ['auto', 'ttest']:
                # t-test
                statistic, p_value = stats.ttest_ind(group_data[0], group_data[1])
                test_name = 'Independent t-test'
            else:
                # Mann-Whitney U test
                statistic, p_value = stats.mannwhitneyu(group_data[0], group_data[1])
                test_name = 'Mann-Whitney U test'
        
        # 그룹이 3개 이상인 경우
        elif len(group_data) > 2:
            if test_type in ['auto', 'anova']:
                # ANOVA
                statistic, p_value = stats.f_oneway(*group_data)
                test_name = 'One-way ANOVA'
            else:
                # Kruskal-Wallis test
                statistic, p_value = stats.kruskal(*group_data)
                test_name = 'Kruskal-Wallis test'
        else:
            self.logger.error("분석할 그룹이 충분하지 않습니다.")
            return {}
        
        # 효과 크기 계산 (Cohen's d for 2 groups)
        effect_size = None
        if len(group_data) == 2:
            pooled_std = np.sqrt(((len(group_data[0])-1)*np.var(group_data[0]) + 
                                (len(group_data[1])-1)*np.var(group_data[1])) / 
                               (len(group_data[0])+len(group_data[1])-2))
            if pooled_std != 0:
                effect_size = (np.mean(group_data[0]) - np.mean(group_data[1])) / pooled_std
        
        results = {
            'test_name': test_name,
            'statistic': statistic,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'effect_size': effect_size,
            'groups': {name: {
                'count': len(groups[name]),
                'mean': np.mean(groups[name]),
                'std': np.std(groups[name])
            } for name in group_names}
        }
        
        self.analysis_results['hypothesis_test'] = results
        self.logger.info(f"가설 검정 완료: {test_name}")
        return results
    
    def generate_insights(self, df: pd.DataFrame) -> List[str]:
        """
        데이터 인사이트 생성
        
        Args:
            df: 입력 DataFrame
            
        Returns:
            인사이트 리스트
        """
        insights = []
        
        # 기본 정보
        insights.append(f"데이터셋 크기: {df.shape[0]:,}행 × {df.shape[1]}열")
        
        # 결측값 정보
        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        if missing_pct > 10:
            insights.append(f"⚠️ 전체 데이터의 {missing_pct:.1f}%가 결측값입니다.")
        
        # 중복값 정보
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            insights.append(f"⚠️ {duplicates:,}개의 중복 행이 발견되었습니다.")
        
        # 수치형 변수 인사이트
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            insights.append(f"📊 {len(numeric_cols)}개의 수치형 변수가 있습니다.")
            
            # 상관관계가 강한 변수 쌍
            if 'correlation' in self.analysis_results:
                strong_corr = self.analysis_results['correlation']['strong_correlations']
                if strong_corr:
                    insights.append(f"🔗 {len(strong_corr)}개의 강한 상관관계가 발견되었습니다.")
        
        # 범주형 변수 인사이트
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols) > 0:
            insights.append(f"📝 {len(cat_cols)}개의 범주형 변수가 있습니다.")
            
            high_cardinality = []
            for col in cat_cols:
                if df[col].nunique() > df.shape[0] * 0.8:
                    high_cardinality.append(col)
            
            if high_cardinality:
                insights.append(f"⚠️ 높은 카디널리티를 가진 변수: {', '.join(high_cardinality)}")
        
        # 이상치 정보
        if 'outliers' in self.analysis_results:
            outlier_cols = []
            for col, methods in self.analysis_results['outliers'].items():
                for method, result in methods.items():
                    if result['outlier_percentage'] > 5:
                        outlier_cols.append(col)
                        break
            
            if outlier_cols:
                insights.append(f"🎯 이상치가 많은 변수: {', '.join(set(outlier_cols))}")
        
        return insights
    
    def export_analysis_report(self, output_path: str = 'analysis_report.json'):
        """
        분석 결과 리포트 내보내기
        
        Args:
            output_path: 출력 파일 경로
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_results': self.analysis_results
        }
        
        try:
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"분석 리포트가 {output_path}에 저장되었습니다.")
            
        except Exception as e:
            self.logger.error(f"리포트 저장 실패: {e}")
