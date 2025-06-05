#!/usr/bin/env python3
"""
토양 데이터 처리기
PostgreSQL에서 추출한 토양 데이터를 화재 시뮬레이션용으로 변환하는 모듈
"""

impor        # 토성별 특성 추가 (texture 컬럼이 있는 경우만)
        if 'texture' in processed_df.columns:
            texture_properties = []
            for texture in processed_df['texture']:
                properties = self.texture_properties.get(texture, {
                    'drainage': 0.5, 'water_holding': 0.5, 'fire_risk': 0.5
                })
                texture_properties.append(properties)
            
            processed_df['texture_drainage'] = [p['drainage'] for p in texture_properties]
            processed_df['water_holding'] = [p['water_holding'] for p in texture_properties]
            processed_df['texture_fire_risk'] = [p['fire_risk'] for p in texture_properties]
        else:
            # texture 컬럼이 없으면 기본값 사용
            processed_df['texture_drainage'] = 0.5
            processed_df['water_holding'] = 0.5
            processed_df['texture_fire_risk'] = 0.5 pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging

class SoilDataProcessor:
    """
    토양 데이터를 화재 시뮬레이션용 매개변수로 변환하는 클래스
    """
    
    def __init__(self):
        """토양 데이터 처리기 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 토양형별 화재 영향 매핑
        self.soil_fire_mapping = {
            # 산림토양
            '갈색산림토': {'moisture_retention': 0.6, 'permeability': 0.7, 'fire_susceptibility': 0.5},
            '적황색토': {'moisture_retention': 0.4, 'permeability': 0.8, 'fire_susceptibility': 0.7},
            '암갈색산림토': {'moisture_retention': 0.7, 'permeability': 0.6, 'fire_susceptibility': 0.4},
            '흑색토': {'moisture_retention': 0.8, 'permeability': 0.5, 'fire_susceptibility': 0.3},
            
            # 평지토양
            '회색토': {'moisture_retention': 0.5, 'permeability': 0.6, 'fire_susceptibility': 0.6},
            '갈색토': {'moisture_retention': 0.6, 'permeability': 0.7, 'fire_susceptibility': 0.5},
            '적색토': {'moisture_retention': 0.3, 'permeability': 0.9, 'fire_susceptibility': 0.8},
            
            # 특수토양
            '습지토': {'moisture_retention': 0.9, 'permeability': 0.2, 'fire_susceptibility': 0.1},
            '사구토': {'moisture_retention': 0.2, 'permeability': 1.0, 'fire_susceptibility': 0.9},
            '암석토': {'moisture_retention': 0.1, 'permeability': 0.3, 'fire_susceptibility': 0.2}
        }
        
        # 토성별 특성
        self.texture_properties = {
            '사토': {'drainage': 0.9, 'water_holding': 0.3, 'fire_risk': 0.8},
            '양사토': {'drainage': 0.8, 'water_holding': 0.4, 'fire_risk': 0.7},
            '사양토': {'drainage': 0.7, 'water_holding': 0.5, 'fire_risk': 0.6},
            '양토': {'drainage': 0.6, 'water_holding': 0.6, 'fire_risk': 0.5},
            '미사토': {'drainage': 0.4, 'water_holding': 0.7, 'fire_risk': 0.4},
            '식양토': {'drainage': 0.5, 'water_holding': 0.7, 'fire_risk': 0.4},
            '미사식양토': {'drainage': 0.3, 'water_holding': 0.8, 'fire_risk': 0.3},
            '식토': {'drainage': 0.2, 'water_holding': 0.9, 'fire_risk': 0.2}
        }
        
        # 배수등급별 화재 위험도
        self.drainage_fire_risk = {
            1: 0.9,  # 매우 양호 (건조하기 쉬움)
            2: 0.8,  # 양호
            3: 0.7,  # 약간 양호
            4: 0.5,  # 보통
            5: 0.3,  # 약간 불량
            6: 0.2,  # 불량
            7: 0.1   # 매우 불량 (습함)
        }
    
    def process_soil_data(self, soil_df: pd.DataFrame) -> pd.DataFrame:
        """
        토양 데이터프레임을 처리하여 화재 관련 매개변수 추가
        
        Args:
            soil_df: 토양 데이터프레임
            
        Returns:
            화재 매개변수가 추가된 데이터프레임
        """
        if soil_df.empty:
            self.logger.warning("빈 토양 데이터프레임")
            return soil_df
        
        processed_df = soil_df.copy()
        
        # 토양형별 특성 매핑
        soil_properties = []
        for soil_type in processed_df['soil_type']:
            properties = self.soil_fire_mapping.get(soil_type, {
                'moisture_retention': 0.5,
                'permeability': 0.5,
                'fire_susceptibility': 0.5
            })
            soil_properties.append(properties)
        
        # 토양 특성 컬럼 추가
        processed_df['moisture_retention'] = [p['moisture_retention'] for p in soil_properties]
        processed_df['soil_permeability'] = [p['permeability'] for p in soil_properties]
        processed_df['fire_susceptibility'] = [p['fire_susceptibility'] for p in soil_properties]
        
        # 토성별 특성 추가
        texture_properties = []
        for texture in processed_df['texture']:
            properties = self.texture_properties.get(texture, {
                'drainage': 0.5, 'water_holding': 0.5, 'fire_risk': 0.5
            })
            texture_properties.append(properties)
        
        processed_df['drainage_capacity'] = [p['drainage'] for p in texture_properties]
        processed_df['water_holding_capacity'] = [p['water_holding'] for p in texture_properties]
        processed_df['texture_fire_risk'] = [p['fire_risk'] for p in texture_properties]
        
        # 배수등급별 화재 위험도
        processed_df['drainage_fire_risk'] = processed_df['drainage'].map(
            lambda x: self.drainage_fire_risk.get(x, 0.5)
        )
        
        # 토양 수분 지수 계산
        processed_df['soil_moisture_index'] = self.calculate_soil_moisture_index(processed_df)
        
        # 종합 토양 화재 위험도 계산
        processed_df['soil_fire_risk'] = self.calculate_soil_fire_risk(processed_df)
        
        # 연료 수분 영향 계수 계산
        processed_df['fuel_moisture_factor'] = self.calculate_fuel_moisture_factor(processed_df)
        
        self.logger.info(f"토양 데이터 처리 완료: {len(processed_df)}건")
        return processed_df
    
    def calculate_soil_moisture_index(self, df: pd.DataFrame) -> pd.Series:
        """
        토양 수분 지수 계산
        
        Args:
            df: 처리된 토양 데이터프레임
            
        Returns:
            토양 수분 지수 (0-100)
        """
        moisture_indices = []
        
        for _, row in df.iterrows():
            index = 50  # 기본값
            
            # 토양 수분 함량 영향
            moisture_content = row.get('moisture_content', 20)
            index += (moisture_content - 20) * 1.5
            
            # 토성별 보수력 영향
            water_holding = row.get('water_holding_capacity', 0.5)
            index += (water_holding - 0.5) * 30
            
            # 배수 등급 영향
            drainage = row.get('drainage', 4)
            index -= (drainage - 4) * 8
            
            # 유기물 함량 영향
            organic_matter = row.get('organic_matter', 3)
            index += (organic_matter - 3) * 5
            
            # 토심 영향
            depth = row.get('depth', 50)
            if depth > 100:
                index += 10
            elif depth < 30:
                index -= 15
            
            # 범위 제한 (0-100)
            index = max(0, min(100, index))
            moisture_indices.append(index)
        
        return pd.Series(moisture_indices)
    
    def calculate_soil_fire_risk(self, df: pd.DataFrame) -> pd.Series:
        """
        종합 토양 화재 위험도 계산
        
        Args:
            df: 처리된 토양 데이터프레임
            
        Returns:
            토양 화재 위험도 (0-100)
        """
        fire_risks = []
        
        for _, row in df.iterrows():
            risk = 50  # 기본값
            
            # 토양형별 화재 취약성
            fire_susceptibility = row.get('fire_susceptibility', 0.5)
            risk += (fire_susceptibility - 0.5) * 40
            
            # 토성별 화재 위험도
            texture_fire_risk = row.get('texture_fire_risk', 0.5)
            risk += (texture_fire_risk - 0.5) * 30
            
            # 배수등급별 위험도
            drainage_risk = row.get('drainage_fire_risk', 0.5)
            risk += (drainage_risk - 0.5) * 20
            
            # 토양 수분 지수 역방향 영향
            moisture_index = row.get('soil_moisture_index', 50)
            risk += (50 - moisture_index) * 0.5
            
            # pH 영향 (극단적 pH는 식생에 악영향)
            ph = row.get('ph', 6.5)
            if ph < 5.0 or ph > 8.0:
                risk += 10
            
            # 용적밀도 영향 (높은 밀도는 뿌리 발달 저해)
            bulk_density = row.get('bulk_density', 1.3)
            if bulk_density > 1.6:
                risk += 15
            
            # 범위 제한 (0-100)
            risk = max(0, min(100, risk))
            fire_risks.append(risk)
        
        return pd.Series(fire_risks)
    
    def calculate_fuel_moisture_factor(self, df: pd.DataFrame) -> pd.Series:
        """
        연료 수분에 대한 토양 영향 계수 계산
        
        Args:
            df: 처리된 토양 데이터프레임
            
        Returns:
            연료 수분 영향 계수 (0.1-2.0)
        """
        factors = []
        
        for _, row in df.iterrows():
            factor = 1.0  # 기본값
            
            # 토양 수분 지수 영향
            moisture_index = row.get('soil_moisture_index', 50)
            if moisture_index > 70:
                factor *= 0.7  # 습한 토양은 연료 수분 증가
            elif moisture_index < 30:
                factor *= 1.4  # 건조한 토양은 연료 수분 감소
            
            # 배수 등급 영향
            drainage = row.get('drainage', 4)
            if drainage <= 2:  # 배수 양호
                factor *= 1.2
            elif drainage >= 6:  # 배수 불량
                factor *= 0.8
            
            # 투수계수 영향
            permeability = row.get('permeability', 5)
            if permeability > 10:  # 높은 투수성
                factor *= 1.1
            elif permeability < 2:  # 낮은 투수성
                factor *= 0.9
            
            # 범위 제한 (0.1-2.0)
            factor = max(0.1, min(2.0, factor))
            factors.append(factor)
        
        return pd.Series(factors)
    
    def create_soil_parameter_grid(self, soil_df: pd.DataFrame,
                                  bounds: Tuple[float, float, float, float],
                                  grid_size: int = 100,
                                  parameter: str = 'soil_fire_risk') -> np.ndarray:
        """
        토양 매개변수를 격자 형태로 변환
        
        Args:
            soil_df: 처리된 토양 데이터프레임
            bounds: (min_lon, min_lat, max_lon, max_lat) 영역 경계
            grid_size: 격자 크기 (grid_size x grid_size)
            parameter: 격자화할 매개변수명
            
        Returns:
            토양 매개변수 격자 (수치 배열)
        """
        min_lon, min_lat, max_lon, max_lat = bounds
        
        # 격자 초기화 (기본값으로)
        default_value = 50 if 'risk' in parameter else 0.5
        param_grid = np.full((grid_size, grid_size), default_value, dtype=float)
        
        # 격자 해상도 계산
        lon_step = (max_lon - min_lon) / grid_size
        lat_step = (max_lat - min_lat) / grid_size
        
        # 각 격자 셀에 토양 매개변수 할당
        for i in range(grid_size):
            for j in range(grid_size):
                # 격자 중심 좌표
                lon = min_lon + (j + 0.5) * lon_step
                lat = max_lat - (i + 0.5) * lat_step  # 위에서 아래로
                
                # 해당 위치의 토양 찾기
                nearby_soil = soil_df[
                    (abs(soil_df['longitude'] - lon) < lon_step) &
                    (abs(soil_df['latitude'] - lat) < lat_step)
                ]
                
                if not nearby_soil.empty:
                    # 가장 가까운 토양의 매개변수 사용
                    closest_idx = nearby_soil.index[0]
                    if parameter in nearby_soil.columns:
                        param_grid[i, j] = nearby_soil.loc[closest_idx, parameter]
        
        self.logger.info(f"토양 {parameter} 격자 생성 완료: {grid_size}x{grid_size}")
        return param_grid
    
    def get_soil_statistics(self, soil_df: pd.DataFrame) -> Dict[str, Any]:
        """
        토양 데이터 통계 정보 생성
        
        Args:
            soil_df: 처리된 토양 데이터프레임
            
        Returns:
            통계 정보 딕셔너리
        """
        if soil_df.empty:
            return {}
        
        stats = {
            'total_areas': len(soil_df),
            'soil_type_distribution': soil_df['soil_type'].value_counts().to_dict(),
            'texture_distribution': soil_df['texture'].value_counts().to_dict(),
            'drainage_distribution': soil_df['drainage'].value_counts().to_dict(),
            'average_soil_fire_risk': soil_df['soil_fire_risk'].mean(),
            'average_moisture_index': soil_df['soil_moisture_index'].mean(),
            'high_fire_risk_soils': len(soil_df[soil_df['soil_fire_risk'] > 70]),
            'low_fire_risk_soils': len(soil_df[soil_df['soil_fire_risk'] < 30]),
            'dry_soils': len(soil_df[soil_df['soil_moisture_index'] < 30]),
            'wet_soils': len(soil_df[soil_df['soil_moisture_index'] > 70])
        }
        
        # 수치 데이터 통계
        numeric_columns = ['ph', 'organic_matter', 'moisture_content', 'bulk_density']
        for col in numeric_columns:
            if col in soil_df.columns:
                stats[f'{col}_mean'] = soil_df[col].mean()
                stats[f'{col}_std'] = soil_df[col].std()
        
        self.logger.info("토양 통계 정보 생성 완료")
        return stats
    
    def classify_soil_fire_hazard(self, soil_df: pd.DataFrame) -> pd.DataFrame:
        """
        토양 화재 위험등급 분류
        
        Args:
            soil_df: 처리된 토양 데이터프레임
            
        Returns:
            위험등급이 추가된 데이터프레임
        """
        df = soil_df.copy()
        
        def classify_hazard(risk_score):
            if risk_score >= 80:
                return '매우높음'
            elif risk_score >= 60:
                return '높음'
            elif risk_score >= 40:
                return '보통'
            elif risk_score >= 20:
                return '낮음'
            else:
                return '매우낮음'
        
        df['soil_fire_hazard_class'] = df['soil_fire_risk'].apply(classify_hazard)
        
        # 위험등급별 색상 코드 추가 (시각화용)
        hazard_colors = {
            '매우높음': '#8B0000',  # 진한 빨강
            '높음': '#FF4500',      # 주황빨강
            '보통': '#FFD700',      # 금색
            '낮음': '#32CD32',      # 연두
            '매우낮음': '#006400'   # 진한 초록
        }
        
        df['hazard_color'] = df['soil_fire_hazard_class'].map(hazard_colors)
        
        self.logger.info("토양 화재 위험등급 분류 완료")
        return df
