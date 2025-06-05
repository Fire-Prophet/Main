#!/usr/bin/env python3
"""
임상도 데이터 처리기
PostgreSQL에서 추출한 임상도 데이터를 화재 시뮬레이션용으로 변환하는 모듈
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging

class ForestDataProcessor:
    """
    임상도 데이터를 화재 시뮬레이션용 연료 모델로 변환하는 클래스
    """
    
    def __init__(self):
        """임상도 데이터 처리기 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # Anderson 13 연료 모델 매핑
        self.anderson13_mapping = {
            # 초지/풀밭 연료 (Grass)
            'GR1': {'name': '짧은 건초지', 'load': 0.1, 'fire_rate': 'very_high'},
            'GR2': {'name': '낮은 풀밭', 'load': 0.2, 'fire_rate': 'high'},
            'GR3': {'name': '중간 풀밭', 'load': 0.3, 'fire_rate': 'high'},
            'GR4': {'name': '높은 풀밭', 'load': 0.5, 'fire_rate': 'very_high'},
            'GR5': {'name': '낮은 관목+풀', 'load': 0.4, 'fire_rate': 'high'},
            'GR6': {'name': '습한 풀밭', 'load': 0.2, 'fire_rate': 'moderate'},
            'GR7': {'name': '높은 풀밭', 'load': 0.8, 'fire_rate': 'very_high'},
            'GR8': {'name': '밀식 풀밭', 'load': 1.5, 'fire_rate': 'extreme'},
            'GR9': {'name': '건조 풀밭', 'load': 1.0, 'fire_rate': 'very_high'},
            
            # 관목 연료 (Shrub)  
            'SH1': {'name': '낮은 관목', 'load': 0.3, 'fire_rate': 'moderate'},
            'SH2': {'name': '중간 관목', 'load': 1.4, 'fire_rate': 'high'},
            'SH3': {'name': '중간-높은 관목', 'load': 0.9, 'fire_rate': 'high'},
            'SH4': {'name': '낮은 습윤관목', 'load': 0.9, 'fire_rate': 'low'},
            'SH5': {'name': '높은 관목', 'load': 3.6, 'fire_rate': 'very_high'},
            'SH6': {'name': '낮은 건조관목', 'load': 2.9, 'fire_rate': 'high'},
            'SH7': {'name': '매우높은 관목', 'load': 5.3, 'fire_rate': 'extreme'},
            'SH8': {'name': '밀식 관목', 'load': 3.0, 'fire_rate': 'high'},
            'SH9': {'name': '건조 밀식관목', 'load': 4.5, 'fire_rate': 'extreme'},
            
            # 목재 연료 (Timber Litter)
            'TL1': {'name': '침엽수 낙엽층', 'load': 1.0, 'fire_rate': 'moderate'},
            'TL2': {'name': '방송 침엽수', 'load': 2.2, 'fire_rate': 'moderate'},
            'TL3': {'name': '중간 낙엽층', 'load': 0.5, 'fire_rate': 'low'},
            'TL4': {'name': '작은 가지 포함', 'load': 0.5, 'fire_rate': 'low'},
            'TL5': {'name': '침엽수 관목', 'load': 1.2, 'fire_rate': 'moderate'},
            'TL6': {'name': '중간-높은 낙엽층', 'load': 2.4, 'fire_rate': 'moderate'},
            'TL7': {'name': '큰 가지 포함', 'load': 0.3, 'fire_rate': 'low'},
            'TL8': {'name': '긴바늘 낙엽층', 'load': 5.8, 'fire_rate': 'low'},
            'TL9': {'name': '활엽수 낙엽층', 'load': 6.6, 'fire_rate': 'moderate'},
            
            # 가지/목재 연료 (Timber Understory)
            'TU1': {'name': '낮은 하층', 'load': 0.5, 'fire_rate': 'low'},
            'TU2': {'name': '중간 하층', 'load': 1.0, 'fire_rate': 'moderate'},
            'TU3': {'name': '중간-높은 하층', 'load': 1.8, 'fire_rate': 'moderate'},
            'TU4': {'name': '높은 하층', 'load': 3.0, 'fire_rate': 'moderate'},
            'TU5': {'name': '매우높은 하층', 'load': 4.0, 'fire_rate': 'high'},
            
            # 베기/잔재 연료 (Slash)
            'SB1': {'name': '얇은 베기잔재', 'load': 1.5, 'fire_rate': 'moderate'},
            'SB2': {'name': '중간 베기잔재', 'load': 4.5, 'fire_rate': 'moderate'},
            'SB3': {'name': '두꺼운 베기잔재', 'load': 5.5, 'fire_rate': 'high'},
            'SB4': {'name': '매우두꺼운 베기잔재', 'load': 5.5, 'fire_rate': 'high'},
            
            # 연료 없음/물
            'NB1': {'name': '도시지역', 'load': 0.0, 'fire_rate': 'none'},
            'NB2': {'name': '암석/맨땅', 'load': 0.0, 'fire_rate': 'none'},
            'NB3': {'name': '물/호수', 'load': 0.0, 'fire_rate': 'none'}
        }
        
        # 한국 임상별 연료 모델 매핑
        self.korean_forest_mapping = {
            # 침엽수림
            '소나무림': 'TL2',       # 방송 침엽수 
            '잣나무림': 'TL1',       # 침엽수 낙엽층
            '낙엽송림': 'TL2',       # 방송 침엽수
            '전나무림': 'TL1',       # 침엽수 낙엽층
            '가문비나무림': 'TL1',   # 침엽수 낙엽층
            '기타침엽수림': 'TL2',   # 방송 침엽수
            
            # 활엽수림  
            '참나무림': 'TL9',       # 활엽수 낙엽층
            '너도밤나무림': 'TL9',   # 활엽수 낙엽층
            '자작나무림': 'TL9',     # 활엽수 낙엽층
            '포플러림': 'TL9',       # 활엽수 낙엽층
            '기타활엽수림': 'TL9',   # 활엽수 낙엽층
            
            # 혼효림
            '침활혼효림': 'TL3',     # 중간 낙엽층
            '활침혼효림': 'TL3',     # 중간 낙엽층
            
            # 특수림
            '대나무림': 'GR8',       # 밀식 풀밭
            '죽림': 'GR8',           # 밀식 풀밭
            
            # 관목/풀지
            '관목림': 'SH2',         # 중간 관목
            '초지': 'GR3',           # 중간 풀밭
            '목초지': 'GR2',         # 낮은 풀밭
            
            # 비연료지역
            '무립목지': 'NB2',       # 암석/맨땅
            '도시': 'NB1',           # 도시지역
            '수계': 'NB3',           # 물/호수
            '도로': 'NB1',           # 도시지역
            '나지': 'NB2'            # 암석/맨땅
        }
    
    def map_forest_to_fuel_model(self, forest_type: str, density: float = 0.5, 
                                 age_class: int = 3) -> str:
        """
        임상 정보를 Anderson 13 연료 모델로 매핑
        
        Args:
            forest_type: 임상 (소나무림, 활엽수림 등)
            density: 밀도 (0.0-1.0)
            age_class: 영급 (1-6영급)
            
        Returns:
            Anderson 13 연료 모델 코드
        """
        # 기본 매핑
        base_fuel = self.korean_forest_mapping.get(forest_type, 'TL2')
        
        # 밀도와 영급을 고려한 조정
        if base_fuel.startswith('TL'):  # 목재 연료인 경우
            if density < 0.3:  # 낮은 밀도
                if age_class <= 2:  # 어린 숲
                    return 'TU1'  # 낮은 하층
                else:
                    return 'TL1'  # 침엽수 낙엽층
            elif density > 0.8:  # 높은 밀도
                if age_class >= 5:  # 노령림
                    return 'TU4'  # 높은 하층
                else:
                    return 'TU2'  # 중간 하층
        
        elif base_fuel.startswith('SH'):  # 관목 연료인 경우  
            if density < 0.3:
                return 'SH1'  # 낮은 관목
            elif density > 0.8:
                return 'SH5'  # 높은 관목
        
        elif base_fuel.startswith('GR'):  # 풀 연료인 경우
            if density < 0.3:
                return 'GR1'  # 짧은 건초지
            elif density > 0.8:
                return 'GR4'  # 높은 풀밭
        
        return base_fuel
    
    def process_forest_dataframe(self, forest_df: pd.DataFrame) -> pd.DataFrame:
        """
        임상도 데이터프레임을 처리하여 연료 모델 정보 추가
        
        Args:
            forest_df: 임상도 데이터프레임
            
        Returns:
            연료 모델 정보가 추가된 데이터프레임
        """
        if forest_df.empty:
            self.logger.warning("빈 임상도 데이터프레임")
            return forest_df
        
        processed_df = forest_df.copy()
        
        # 연료 모델 매핑
        processed_df['fuel_model'] = processed_df.apply(
            lambda row: self.map_forest_to_fuel_model(
                forest_type=row.get('forest_type', '소나무림'),
                density=row.get('density', 0.5),
                age_class=row.get('age_class', 3)
            ), axis=1
        )
        
        # Anderson 13 연료 특성 추가
        fuel_properties = []
        for fuel_code in processed_df['fuel_model']:
            properties = self.anderson13_mapping.get(fuel_code, {
                'name': '알 수 없음', 'load': 0.5, 'fire_rate': 'moderate'
            })
            fuel_properties.append(properties)
        
        # 연료 특성 컬럼 추가
        processed_df['fuel_name'] = [p['name'] for p in fuel_properties]
        processed_df['fuel_load'] = [p['load'] for p in fuel_properties]
        processed_df['fire_rate'] = [p['fire_rate'] for p in fuel_properties]
        
        # 추가 화재 위험도 계산
        processed_df['fire_risk_score'] = self.calculate_fire_risk_score(processed_df)
        
        self.logger.info(f"임상도 데이터 처리 완료: {len(processed_df)}건")
        return processed_df
    
    def calculate_fire_risk_score(self, df: pd.DataFrame) -> pd.Series:
        """
        임상 조건을 기반으로 화재 위험도 점수 계산
        
        Args:
            df: 처리된 임상도 데이터프레임
            
        Returns:
            화재 위험도 점수 (0-100)
        """
        risk_scores = []
        
        for _, row in df.iterrows():
            score = 50  # 기본 점수
            
            # 연료 타입별 위험도
            fire_rate = row.get('fire_rate', 'moderate')
            if fire_rate == 'extreme':
                score += 30
            elif fire_rate == 'very_high':
                score += 20
            elif fire_rate == 'high':
                score += 10
            elif fire_rate == 'low':
                score -= 10
            elif fire_rate == 'none':
                score = 0
            
            # 밀도 영향
            density = row.get('density', 0.5)
            if density > 0.8:
                score += 15
            elif density < 0.3:
                score -= 10
            
            # 영급 영향
            age_class = row.get('age_class', 3)
            if age_class <= 2:  # 어린 숲
                score += 5
            elif age_class >= 5:  # 노령림
                score += 10
            
            # 수관피복도 영향
            canopy_cover = row.get('canopy_cover', 50)
            if canopy_cover > 80:
                score -= 5  # 수관피복이 높으면 바람 차단
            elif canopy_cover < 30:
                score += 10  # 수관피복이 낮으면 건조
            
            # 점수 범위 제한 (0-100)
            score = max(0, min(100, score))
            risk_scores.append(score)
        
        return pd.Series(risk_scores)
    
    def create_fuel_grid(self, forest_df: pd.DataFrame, 
                        bounds: Tuple[float, float, float, float],
                        grid_size: int = 100) -> np.ndarray:
        """
        임상도 데이터를 격자 형태의 연료 맵으로 변환
        
        Args:
            forest_df: 처리된 임상도 데이터프레임
            bounds: (min_lon, min_lat, max_lon, max_lat) 영역 경계
            grid_size: 격자 크기 (grid_size x grid_size)
            
        Returns:
            연료 모델 격자 (문자열 배열)
        """
        min_lon, min_lat, max_lon, max_lat = bounds
        
        # 격자 초기화
        fuel_grid = np.full((grid_size, grid_size), 'NB2', dtype='U4')
        
        # 격자 해상도 계산
        lon_step = (max_lon - min_lon) / grid_size
        lat_step = (max_lat - min_lat) / grid_size
        
        # 각 격자 셀에 연료 모델 할당
        for i in range(grid_size):
            for j in range(grid_size):
                # 격자 중심 좌표
                lon = min_lon + (j + 0.5) * lon_step
                lat = max_lat - (i + 0.5) * lat_step  # 위에서 아래로
                
                # 해당 위치의 임상 찾기
                nearby_forest = forest_df[
                    (abs(forest_df['longitude'] - lon) < lon_step) &
                    (abs(forest_df['latitude'] - lat) < lat_step)
                ]
                
                if not nearby_forest.empty:
                    # 가장 가까운 임상의 연료 모델 사용
                    closest_idx = nearby_forest.index[0]
                    fuel_model = nearby_forest.loc[closest_idx, 'fuel_model']
                    fuel_grid[i, j] = fuel_model
        
        self.logger.info(f"연료 격자 생성 완료: {grid_size}x{grid_size}")
        return fuel_grid
    
    def get_fuel_statistics(self, forest_df: pd.DataFrame) -> Dict[str, Any]:
        """
        임상도 연료 모델 통계 정보 생성
        
        Args:
            forest_df: 처리된 임상도 데이터프레임
            
        Returns:
            통계 정보 딕셔너리
        """
        if forest_df.empty:
            return {}
        
        stats = {
            'total_areas': len(forest_df),
            'fuel_model_distribution': forest_df['fuel_model'].value_counts().to_dict(),
            'forest_type_distribution': forest_df['forest_type'].value_counts().to_dict(),
            'fire_rate_distribution': forest_df['fire_rate'].value_counts().to_dict(),
            'average_fire_risk': forest_df['fire_risk_score'].mean(),
            'max_fire_risk': forest_df['fire_risk_score'].max(),
            'min_fire_risk': forest_df['fire_risk_score'].min(),
            'high_risk_areas': len(forest_df[forest_df['fire_risk_score'] > 70]),
            'low_risk_areas': len(forest_df[forest_df['fire_risk_score'] < 30])
        }
        
        self.logger.info("임상도 통계 정보 생성 완료")
        return stats
