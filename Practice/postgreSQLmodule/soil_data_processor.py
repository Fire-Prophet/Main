#!/usr/bin/env python3
"""
🌱 토양 데이터 처리기 (Soil Data Processor)
==========================================

PostgreSQL에서 추출한 토양 관리 데이터를 화재 시뮬레이션용으로 변환하는 모듈입니다.
토양 수분, 배수성, 화재 위험도 등을 계산하여 연료 수분 함량 예측에 활용합니다.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
import logging


class SoilDataProcessor:
    """토양 데이터를 화재 시뮬레이션용 매개변수로 변환하는 클래스"""
    
    def __init__(self):
        """토양 데이터 처리기 초기화"""
        self.logger = self._setup_logger()
        
        # 토양 타입별 특성 정의
        self.soil_types = {
            '사질토': {'drainage': 0.9, 'water_holding': 0.3, 'fire_risk': 0.8},
            '사양토': {'drainage': 0.7, 'water_holding': 0.5, 'fire_risk': 0.6},
            '양토': {'drainage': 0.6, 'water_holding': 0.7, 'fire_risk': 0.4},
            '식양토': {'drainage': 0.4, 'water_holding': 0.8, 'fire_risk': 0.3},
            '식토': {'drainage': 0.2, 'water_holding': 0.9, 'fire_risk': 0.2}
        }
    
    def _setup_logger(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger('SoilDataProcessor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def process_soil_data(self, soil_df: pd.DataFrame) -> pd.DataFrame:
        """토양 관리 데이터를 화재 시뮬레이션용으로 처리"""
        if soil_df.empty:
            self.logger.warning("빈 토양 데이터프레임")
            return soil_df
        
        try:
            processed_df = soil_df.copy()
            
            # 토양 타입 정규화 및 특성 매핑
            processed_df = self._map_soil_properties(processed_df)
            
            # 연료 수분 함량 계산
            processed_df['fuel_moisture_factor'] = self._calculate_fuel_moisture_factor(processed_df)
            
            # 화재 위험도 계산
            processed_df['fire_risk_score'] = self._calculate_fire_risk_score(processed_df)
            
            self.logger.info(f"토양 데이터 처리 완료: {len(processed_df)}개 레코드")
            return processed_df
            
        except Exception as e:
            self.logger.error(f"토양 데이터 처리 실패: {e}")
            return soil_df
    
    def _map_soil_properties(self, df: pd.DataFrame) -> pd.DataFrame:
        """토양 타입을 기반으로 속성 매핑"""
        processed_df = df.copy()
        
        # 토양 타입별 특성 추가
        if 'soil_type' in processed_df.columns:
            soil_properties = []
            for soil_type in processed_df['soil_type']:
                normalized_type = self._normalize_soil_type(soil_type)
                properties = self.soil_types.get(normalized_type, {
                    'drainage': 0.5, 'water_holding': 0.5, 'fire_risk': 0.5
                })
                soil_properties.append(properties)
            
            processed_df['drainage_capacity'] = [p['drainage'] for p in soil_properties]
            processed_df['water_holding_capacity'] = [p['water_holding'] for p in soil_properties]
            processed_df['base_fire_risk'] = [p['fire_risk'] for p in soil_properties]
        
        return processed_df
    
    def _normalize_soil_type(self, soil_type: str) -> str:
        """토양 타입 정규화"""
        if pd.isna(soil_type):
            return '양토'
        
        soil_type = str(soil_type).strip()
        
        # 영어 -> 한글 변환
        eng_to_kor = {
            'sand': '사질토',
            'sandy loam': '사양토', 
            'loam': '양토',
            'clay loam': '식양토',
            'clay': '식토'
        }
        
        normalized = eng_to_kor.get(soil_type.lower(), soil_type)
        
        if normalized in self.soil_types:
            return normalized
        else:
            return '양토'
    
    def _calculate_fuel_moisture_factor(self, df: pd.DataFrame) -> pd.Series:
        """연료 수분 함량 인자 계산"""
        base_moisture = 0.3
        
        if 'water_holding_capacity' in df.columns:
            moisture_factor = base_moisture + (df['water_holding_capacity'] - 0.5) * 0.2
        else:
            moisture_factor = pd.Series([base_moisture] * len(df))
        
        # 유기물 함량 고려 (있는 경우)
        if 'organic_matter' in df.columns:
            organic_effect = (df['organic_matter'] / 100) * 0.1
            moisture_factor += organic_effect
        
        return moisture_factor.clip(0.1, 0.8)
    
    def _calculate_fire_risk_score(self, df: pd.DataFrame) -> pd.Series:
        """토양 기반 화재 위험도 점수 계산"""
        base_risk = df.get('base_fire_risk', pd.Series([0.5] * len(df)))
        
        # 배수성이 좋을수록 화재 위험 증가
        if 'drainage_capacity' in df.columns:
            drainage_risk = df['drainage_capacity'] * 0.3
        else:
            drainage_risk = pd.Series([0.15] * len(df))
        
        fire_risk = base_risk + drainage_risk
        return fire_risk.clip(0, 1)
    
    def create_soil_grid(self, soil_df: pd.DataFrame, 
                        grid_size: Tuple[int, int],
                        bounding_box: Tuple[float, float, float, float],
                        parameter: str = 'fuel_moisture_factor') -> np.ndarray:
        """토양 데이터를 격자로 변환"""
        if soil_df.empty:
            default_values = {
                'fuel_moisture_factor': 0.3,
                'fire_risk_score': 0.5
            }
            default_value = default_values.get(parameter, 0.5)
            return np.full(grid_size, default_value)
        
        rows, cols = grid_size
        grid = np.full(grid_size, 0.3)  # 기본값으로 초기화
        
        # 간단한 격자 채우기 (실제로는 공간 좌표 기반으로 해야 함)
        if parameter in soil_df.columns:
            mean_value = soil_df[parameter].mean()
            grid.fill(mean_value)
        
        return grid
    
    def get_soil_statistics(self, soil_df: pd.DataFrame) -> Dict[str, Any]:
        """토양 데이터 통계 정보 반환"""
        if soil_df.empty:
            return {'status': 'empty', 'count': 0}
        
        stats = {'count': len(soil_df)}
        
        # 화재 위험도 통계
        if 'fire_risk_score' in soil_df.columns:
            fire_risk = soil_df['fire_risk_score']
            stats['fire_risk'] = {
                'mean': float(fire_risk.mean()),
                'min': float(fire_risk.min()),
                'max': float(fire_risk.max())
            }
        
        return stats


if __name__ == "__main__":
    # 테스트 코드
    print("🌱 토양 데이터 처리기 테스트")
    
    test_data = {
        'id': [1, 2, 3],
        'soil_type': ['사질토', '양토', '식양토'],
        'organic_matter': [2.5, 4.1, 3.8]
    }
    
    soil_df = pd.DataFrame(test_data)
    processor = SoilDataProcessor()
    processed_df = processor.process_soil_data(soil_df)
    
    print(f"✅ 처리된 토양 데이터: {len(processed_df)}개")
    print("📊 화재 위험도:", processed_df['fire_risk_score'].round(3).tolist())
    print("💧 수분 인자:", processed_df['fuel_moisture_factor'].round(3).tolist())
