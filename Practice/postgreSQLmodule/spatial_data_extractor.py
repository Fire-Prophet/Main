#!/usr/bin/env python3
"""
공간 데이터 추출기
PostgreSQL/PostGIS에서 임상도, 토양, 지형 데이터를 추출하는 모듈
"""

import psycopg2
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from pathlib import Path
import json

class SpatialDataExtractor:
    """
    PostgreSQL/PostGIS에서 화재 시뮬레이션용 공간 데이터를 추출하는 클래스
    """
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        공간 데이터 추출기 초기화
        
        Args:
            db_config: 데이터베이스 연결 설정
        """
        self.db_config = db_config
        self.connection = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """PostgreSQL 데이터베이스 연결"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.logger.info("PostgreSQL 연결 성공")
            return True
        except Exception as e:
            self.logger.error(f"PostgreSQL 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.connection:
            self.connection.close()
            self.logger.info("PostgreSQL 연결 해제")
    
    def extract_forest_data(self, bounds: Tuple[float, float, float, float]) -> pd.DataFrame:
        """
        임상도 데이터 추출
        
        Args:
            bounds: (min_lon, min_lat, max_lon, max_lat) 경계 좌표
            
        Returns:
            임상도 데이터프레임 (임상, 수종, 밀도 등)
        """
        min_lon, min_lat, max_lon, max_lat = bounds
        
        query = """
        SELECT 
            id,
            ST_AsText(geom) as geometry,
            forest_type,     -- 임상 (소나무림, 활엽수림, 혼효림 등)
            tree_species,    -- 수종
            density,         -- 밀도 (0.0-1.0)
            age_class,       -- 영급 (1-6영급)
            fuel_code,       -- 연료 분류 코드
            canopy_cover,    -- 수관피복도 (%)
            dbh_avg,         -- 평균 흉고직경 (cm)
            height_avg,      -- 평균 수고 (m)
            ST_X(ST_Centroid(geom)) as longitude,
            ST_Y(ST_Centroid(geom)) as latitude
        FROM forest_management 
        WHERE geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
        """
        
        try:
            df = pd.read_sql_query(
                query, 
                self.connection, 
                params=(min_lon, min_lat, max_lon, max_lat)
            )
            self.logger.info(f"임상도 데이터 {len(df)}건 추출 완료")
            return df
        except Exception as e:
            self.logger.error(f"임상도 데이터 추출 실패: {e}")
            return pd.DataFrame()
    
    def extract_soil_data(self, bounds: Tuple[float, float, float, float]) -> pd.DataFrame:
        """
        토양 데이터 추출
        
        Args:
            bounds: (min_lon, min_lat, max_lon, max_lat) 경계 좌표
            
        Returns:
            토양 데이터프레임 (토성, 배수, 수분 등)
        """
        min_lon, min_lat, max_lon, max_lat = bounds
        
        query = """
        SELECT 
            id,
            ST_AsText(geom) as geometry,
            soil_type,        -- 토양형 (갈색산림토, 적황색토 등)
            texture,          -- 토성 (사토, 양토, 점토 등)
            drainage,         -- 배수등급 (1-7)
            depth,            -- 토심 (cm)
            ph,               -- 산도 
            organic_matter,   -- 유기물 함량 (%)
            moisture_content, -- 수분 함량 (%)
            bulk_density,     -- 용적밀도 (g/cm³)
            permeability,     -- 투수계수 (cm/hr)
            ST_X(ST_Centroid(geom)) as longitude,
            ST_Y(ST_Centroid(geom)) as latitude
        FROM soil_management 
        WHERE geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
        """
        
        try:
            df = pd.read_sql_query(
                query, 
                self.connection, 
                params=(min_lon, min_lat, max_lon, max_lat)
            )
            self.logger.info(f"토양 데이터 {len(df)}건 추출 완료")
            return df
        except Exception as e:
            self.logger.error(f"토양 데이터 추출 실패: {e}")
            return pd.DataFrame()
    
    def extract_elevation_data(self, bounds: Tuple[float, float, float, float]) -> pd.DataFrame:
        """
        지형 데이터 추출 (고도, 경사도, 향)
        
        Args:
            bounds: (min_lon, min_lat, max_lon, max_lat) 경계 좌표
            
        Returns:
            지형 데이터프레임
        """
        min_lon, min_lat, max_lon, max_lat = bounds
        
        query = """
        SELECT 
            id,
            ST_X(location) as longitude,
            ST_Y(location) as latitude,
            elevation,        -- 고도 (m)
            slope,           -- 경사도 (도)
            aspect,          -- 향 (도, 0-360)
            curvature,       -- 곡률
            tpi,             -- 지형위치지수
            tri             -- 지형거칠기지수
        FROM elevation_data 
        WHERE location && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
        ORDER BY longitude, latitude
        """
        
        try:
            df = pd.read_sql_query(
                query, 
                self.connection, 
                params=(min_lon, min_lat, max_lon, max_lat)
            )
            self.logger.info(f"지형 데이터 {len(df)}건 추출 완료")
            return df
        except Exception as e:
            self.logger.error(f"지형 데이터 추출 실패: {e}")
            return pd.DataFrame()
    
    def extract_weather_stations(self, bounds: Tuple[float, float, float, float]) -> pd.DataFrame:
        """
        기상 관측소 데이터 추출
        
        Args:
            bounds: (min_lon, min_lat, max_lon, max_lat) 경계 좌표
            
        Returns:
            기상 데이터프레임
        """
        min_lon, min_lat, max_lon, max_lat = bounds
        
        query = """
        SELECT 
            station_id,
            station_name,
            ST_X(location) as longitude,
            ST_Y(location) as latitude,
            elevation as station_elevation,
            temperature,      -- 기온 (°C)
            humidity,         -- 습도 (%)
            wind_speed,       -- 풍속 (m/s)
            wind_direction,   -- 풍향 (도)
            precipitation,    -- 강수량 (mm)
            pressure,         -- 기압 (hPa)
            observation_time  -- 관측 시간
        FROM weather_stations 
        WHERE location && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
        AND observation_time >= NOW() - INTERVAL '24 hours'
        ORDER BY observation_time DESC
        """
        
        try:
            df = pd.read_sql_query(
                query, 
                self.connection, 
                params=(min_lon, min_lat, max_lon, max_lat)
            )
            self.logger.info(f"기상 데이터 {len(df)}건 추출 완료")
            return df
        except Exception as e:
            self.logger.error(f"기상 데이터 추출 실패: {e}")
            return pd.DataFrame()
    
    def get_spatial_bounds_for_region(self, region_name: str) -> Optional[Tuple[float, float, float, float]]:
        """
        지역명으로 공간 경계 좌표 조회
        
        Args:
            region_name: 지역명 (예: '강원도', '경기도 안양시' 등)
            
        Returns:
            (min_lon, min_lat, max_lon, max_lat) 또는 None
        """
        query = """
        SELECT 
            ST_XMin(geom) as min_lon,
            ST_YMin(geom) as min_lat,
            ST_XMax(geom) as max_lon,
            ST_YMax(geom) as max_lat
        FROM administrative_boundaries 
        WHERE region_name ILIKE %s
        LIMIT 1
        """
        
        try:
            result = pd.read_sql_query(
                query, 
                self.connection, 
                params=(f'%{region_name}%',)
            )
            
            if len(result) > 0:
                row = result.iloc[0]
                bounds = (row['min_lon'], row['min_lat'], row['max_lon'], row['max_lat'])
                self.logger.info(f"지역 '{region_name}' 경계: {bounds}")
                return bounds
            else:
                self.logger.warning(f"지역 '{region_name}'을 찾을 수 없습니다")
                return None
                
        except Exception as e:
            self.logger.error(f"지역 경계 조회 실패: {e}")
            return None
    
    def extract_all_spatial_data(self, bounds: Tuple[float, float, float, float]) -> Dict[str, pd.DataFrame]:
        """
        지정된 영역의 모든 공간 데이터를 한번에 추출
        
        Args:
            bounds: (min_lon, min_lat, max_lon, max_lat) 경계 좌표
            
        Returns:
            각 데이터 타입별 데이터프레임 딕셔너리
        """
        if not self.connection:
            if not self.connect():
                return {}
        
        all_data = {}
        
        # 임상도 데이터
        all_data['forest'] = self.extract_forest_data(bounds)
        
        # 토양 데이터  
        all_data['soil'] = self.extract_soil_data(bounds)
        
        # 지형 데이터
        all_data['elevation'] = self.extract_elevation_data(bounds)
        
        # 기상 데이터
        all_data['weather'] = self.extract_weather_stations(bounds)
        
        self.logger.info(f"모든 공간 데이터 추출 완료")
        return all_data
    
    def save_extracted_data(self, data: Dict[str, pd.DataFrame], output_dir: str):
        """
        추출된 데이터를 파일로 저장
        
        Args:
            data: 추출된 데이터 딕셔너리
            output_dir: 저장할 디렉토리 경로
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for data_type, df in data.items():
            if not df.empty:
                # CSV 저장
                csv_path = output_path / f"{data_type}_data.csv"
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                
                # JSON 저장  
                json_path = output_path / f"{data_type}_data.json"
                df.to_json(json_path, orient='records', ensure_ascii=False, indent=2)
                
                self.logger.info(f"{data_type} 데이터 저장: {csv_path}, {json_path}")
