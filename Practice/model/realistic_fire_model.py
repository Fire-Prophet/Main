"""
화재 시뮬레이션 현실성 향상 모듈
- 스포팅(비화) 현상 모델링
- 화재 행동 복잡성 증가
- 인간 활동 영향 고려
- 계절별/시간대별 특성 반영
- 상세한 연료 수분 모델링
- 화재 억제 활동 시뮬레이션
"""

import numpy as np
import pandas as pd
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from enum import Enum

class FireBehaviorType(Enum):
    """화재 행동 유형"""
    SURFACE = "surface"          # 표면화재
    CROWN = "crown"              # 수관화재
    GROUND = "ground"            # 지중화재
    SPOTTING = "spotting"        # 비화
    EMBER_STORM = "ember_storm"  # 불꽃 폭풍

class SuppressionType(Enum):
    """진압 활동 유형"""
    GROUND_CREW = "ground_crew"      # 지상 소방대
    AERIAL_DROP = "aerial_drop"      # 항공 살수
    FIRE_RETARDANT = "fire_retardant" # 소화제
    FIREBREAK = "firebreak"          # 방화선
    CONTROLLED_BURN = "controlled_burn" # 역화

@dataclass
class HumanActivity:
    """인간 활동 데이터"""
    population_density: float       # 인구 밀도
    road_density: float            # 도로 밀도
    recreation_areas: List[Tuple[int, int]]  # 레크리에이션 지역
    industrial_sites: List[Tuple[int, int]]   # 산업 시설
    power_lines: List[Tuple[int, int, int, int]]  # 전력선 (x1,y1,x2,y2)
    ignition_risk_map: np.ndarray = field(default=None)  # 착화 위험도 맵

@dataclass
class DetailedWeatherConditions:
    """상세 기상 조건"""
    temperature: float              # 온도 (°C)
    relative_humidity: float        # 상대습도 (%)
    wind_speed: float              # 풍속 (m/s)
    wind_direction: float          # 풍향 (도, 북쪽=0)
    atmospheric_pressure: float     # 기압 (hPa)
    solar_radiation: float         # 일사량 (W/m²)
    precipitation: float           # 강수량 (mm)
    drought_index: float           # 가뭄 지수
    fire_weather_index: float      # 화재 기상 지수
    stability_class: str           # 대기 안정도 등급

class RealisticFireModel:
    """현실적 화재 모델링 클래스"""
    
    def __init__(self, grid_size: Tuple[int, int], cell_size: float = 30.0):
        """
        Args:
            grid_size: 격자 크기 (height, width)
            cell_size: 셀 크기 (미터)
        """
        self.height, self.width = grid_size
        self.cell_size = cell_size
        
        # 초기화
        self.fuel_map = None
        self.fuel_moisture_map = None
        self.elevation_map = None
        self.human_activity = None
        self.weather_conditions = None
        
        # 화재 상태 맵들
        self.fire_intensity_map = np.zeros(grid_size, dtype=np.float32)
        self.burn_probability_map = np.zeros(grid_size, dtype=np.float32)
        self.flame_length_map = np.zeros(grid_size, dtype=np.float32)
        self.heat_flux_map = np.zeros(grid_size, dtype=np.float32)
        self.ember_source_map = np.zeros(grid_size, dtype=np.float32)
        
        # 화재 행동 추적
        self.fire_behavior_history = []
        self.spotting_events = []
        self.suppression_activities = []
        
    def set_fuel_moisture_model(self, base_moisture: Dict[str, float], 
                               daily_variation: float = 0.05,
                               seasonal_factor: float = 1.0):
        """상세한 연료 수분 모델 설정"""
        if self.fuel_map is None:
            raise ValueError("연료 맵을 먼저 설정해야 합니다")
        
        self.fuel_moisture_map = np.zeros_like(self.fuel_map, dtype=np.float32)
        
        # 시간과 위치에 따른 수분 변화 모델링
        for i in range(self.height):
            for j in range(self.width):
                fuel_type = self.fuel_map[i, j]
                
                # 기본 수분량
                base_val = base_moisture.get(str(fuel_type), 0.15)
                
                # 지형 효과 (고도, 경사면)
                if self.elevation_map is not None:
                    elevation_factor = 1.0 + (self.elevation_map[i, j] - 500) / 1000 * 0.1
                else:
                    elevation_factor = 1.0
                
                # 미세 기후 효과 (무작위 변동)
                microclimate_factor = 1.0 + np.random.normal(0, daily_variation)
                
                # 최종 수분량 계산
                moisture = base_val * elevation_factor * microclimate_factor * seasonal_factor
                self.fuel_moisture_map[i, j] = np.clip(moisture, 0.05, 0.50)
    
    def calculate_fire_behavior(self, current_grid: np.ndarray) -> Dict[str, np.ndarray]:
        """화재 행동 특성 계산"""
        fire_mask = (current_grid == 1)  # 현재 연소 중인 지역
        
        # 화재 강도 계산 (kW/m)
        self.fire_intensity_map = self._calculate_fire_intensity(fire_mask)
        
        # 화염 길이 계산 (m)
        self.flame_length_map = self._calculate_flame_length(self.fire_intensity_map)
        
        # 열 유속 계산 (kW/m²)
        self.heat_flux_map = self._calculate_heat_flux(self.fire_intensity_map, self.flame_length_map)
        
        # 비화 가능성 계산
        self.ember_source_map = self._calculate_ember_production(self.fire_intensity_map, self.flame_length_map)
        
        # 화재 행동 유형 분류
        behavior_types = self._classify_fire_behavior(self.fire_intensity_map, self.flame_length_map)
        
        return {
            'fire_intensity': self.fire_intensity_map,
            'flame_length': self.flame_length_map,
            'heat_flux': self.heat_flux_map,
            'ember_source': self.ember_source_map,
            'behavior_types': behavior_types
        }
    
    def simulate_spotting(self, current_grid: np.ndarray, max_spot_distance: float = 1000) -> List[Tuple[int, int]]:
        """비화(spotting) 현상 시뮬레이션"""
        new_ignitions = []
        
        if self.weather_conditions is None:
            return new_ignitions
        
        # 바람이 강할 때만 비화 고려
        if self.weather_conditions.wind_speed < 5.0:
            return new_ignitions
        
        fire_locations = np.where(current_grid == 1)
        
        for i, j in zip(fire_locations[0], fire_locations[1]):
            # 비화 확률 계산
            ember_potential = self.ember_source_map[i, j]
            spot_probability = self._calculate_spotting_probability(i, j, ember_potential)
            
            if random.random() < spot_probability:
                # 비화 착지점 계산
                landing_points = self._calculate_ember_trajectory(i, j, max_spot_distance)
                
                for land_x, land_y in landing_points:
                    if (0 <= land_x < self.height and 0 <= land_y < self.width and
                        current_grid[land_x, land_y] == 0):  # 연소되지 않은 지역
                        
                        # 착화 성공 확률
                        ignition_prob = self._calculate_ignition_probability(land_x, land_y)
                        
                        if random.random() < ignition_prob:
                            new_ignitions.append((land_x, land_y))
                            
                            # 비화 이벤트 기록
                            self.spotting_events.append({
                                'source': (i, j),
                                'landing': (land_x, land_y),
                                'distance': np.sqrt((land_x - i)**2 + (land_y - j)**2) * self.cell_size,
                                'wind_speed': self.weather_conditions.wind_speed,
                                'wind_direction': self.weather_conditions.wind_direction
                            })
        
        return new_ignitions
    
    def apply_human_influence(self, current_grid: np.ndarray) -> np.ndarray:
        """인간 활동의 영향 적용"""
        if self.human_activity is None:
            return current_grid
        
        modified_grid = current_grid.copy()
        
        # 인간 착화 위험
        if self.human_activity.ignition_risk_map is not None:
            risk_threshold = 0.8
            high_risk_areas = self.human_activity.ignition_risk_map > risk_threshold
            
            # 높은 위험 지역에서 무작위 착화
            for i, j in zip(*np.where(high_risk_areas)):
                if modified_grid[i, j] == 0 and random.random() < 0.001:  # 낮은 확률
                    modified_grid[i, j] = 1
        
        # 도로 근처에서의 착화 위험 증가
        road_ignition_prob = self.human_activity.road_density * 0.0001
        
        # 전력선 근처에서의 착화 위험
        for x1, y1, x2, y2 in self.human_activity.power_lines:
            # 전력선 주변 지역에 착화 위험 추가
            line_cells = self._get_line_cells(x1, y1, x2, y2)
            for i, j in line_cells:
                if (0 <= i < self.height and 0 <= j < self.width and
                    modified_grid[i, j] == 0 and random.random() < 0.0005):
                    modified_grid[i, j] = 1
        
        return modified_grid
    
    def simulate_suppression_activities(self, current_grid: np.ndarray, 
                                      suppression_resources: Dict[str, Any]) -> np.ndarray:
        """진압 활동 시뮬레이션"""
        modified_grid = current_grid.copy()
        
        # 지상 소방대 활동
        if 'ground_crews' in suppression_resources:
            modified_grid = self._apply_ground_suppression(modified_grid, suppression_resources['ground_crews'])
        
        # 항공 살수
        if 'aerial_drops' in suppression_resources:
            modified_grid = self._apply_aerial_suppression(modified_grid, suppression_resources['aerial_drops'])
        
        # 방화선 구축
        if 'firebreaks' in suppression_resources:
            modified_grid = self._apply_firebreaks(modified_grid, suppression_resources['firebreaks'])
        
        # 화재진압제 살포
        if 'retardant_drops' in suppression_resources:
            modified_grid = self._apply_retardant(modified_grid, suppression_resources['retardant_drops'])
        
        return modified_grid
    
    def calculate_seasonal_effects(self, current_date: datetime) -> Dict[str, float]:
        """계절별 효과 계산"""
        month = current_date.month
        day_of_year = current_date.timetuple().tm_yday
        
        # 계절별 화재 위험도 (북반구 기준)
        seasonal_risk = {
            'spring': 0.6 + 0.4 * np.sin(np.pi * (day_of_year - 80) / 92),  # 3-5월
            'summer': 0.8 + 0.2 * np.sin(np.pi * (day_of_year - 172) / 92), # 6-8월
            'autumn': 0.7 + 0.3 * np.sin(np.pi * (day_of_year - 264) / 92), # 9-11월
            'winter': 0.3 + 0.2 * np.sin(np.pi * (day_of_year - 355) / 92)  # 12-2월
        }
        
        if 3 <= month <= 5:
            risk_factor = seasonal_risk['spring']
        elif 6 <= month <= 8:
            risk_factor = seasonal_risk['summer']
        elif 9 <= month <= 11:
            risk_factor = seasonal_risk['autumn']
        else:
            risk_factor = seasonal_risk['winter']
        
        # 일중 변화 (오후 2-4시가 최고 위험)
        hour = current_date.hour
        diurnal_factor = 0.5 + 0.5 * np.sin(np.pi * (hour - 6) / 12)
        
        return {
            'seasonal_risk': float(np.clip(risk_factor, 0.1, 1.0)),
            'diurnal_factor': float(np.clip(diurnal_factor, 0.3, 1.0)),
            'combined_factor': float(np.clip(risk_factor * diurnal_factor, 0.1, 1.0))
        }
    
    def _calculate_fire_intensity(self, fire_mask: np.ndarray) -> np.ndarray:
        """화재 강도 계산 (Byram's 공식 적용)"""
        intensity_map = np.zeros_like(fire_mask, dtype=np.float32)
        
        if self.fuel_map is None:
            return intensity_map
        
        # 연료별 기본 강도 값 (kW/m)
        fuel_intensity = {
            'TL1': 50,   # 낮은 강도 목재
            'TL2': 100,  # 중간 강도 목재  
            'TL3': 200,  # 높은 강도 목재
            'TU1': 80,   # 낮은 관목
            'TU2': 150,  # 높은 관목
            'GS1': 30,   # 짧은 풀
            'GS2': 60,   # 중간 풀
            'GS3': 90,   # 높은 풀
            'GR1': 40,   # 짧은 건조 풀
            'GR2': 70,   # 중간 건조 풀
            'SB1': 120,  # 낮은 관목-풀
            'SB2': 180,  # 중간 관목-풀
            'TU3': 250   # 매우 높은 관목
        }
        
        for i, j in zip(*np.where(fire_mask)):
            fuel_type = str(self.fuel_map[i, j])
            base_intensity = fuel_intensity.get(fuel_type, 75)
            
            # 연료 수분 효과
            if self.fuel_moisture_map is not None:
                moisture_factor = 1.0 - 2.0 * self.fuel_moisture_map[i, j]
                moisture_factor = np.clip(moisture_factor, 0.1, 1.0)
            else:
                moisture_factor = 1.0
            
            # 기상 효과
            weather_factor = 1.0
            if self.weather_conditions is not None:
                # 풍속 효과
                wind_factor = 1.0 + self.weather_conditions.wind_speed / 20.0
                
                # 습도 효과
                humidity_factor = 1.0 - self.weather_conditions.relative_humidity / 200.0
                humidity_factor = np.clip(humidity_factor, 0.3, 1.0)
                
                weather_factor = wind_factor * humidity_factor
            
            intensity_map[i, j] = base_intensity * moisture_factor * weather_factor
        
        return intensity_map
    
    def _calculate_flame_length(self, intensity_map: np.ndarray) -> np.ndarray:
        """화염 길이 계산 (Byram's 공식)"""
        # Flame length (m) = 0.0775 * I^0.46
        # I는 화재 강도 (kW/m)
        flame_length = np.zeros_like(intensity_map)
        non_zero_mask = intensity_map > 0
        flame_length[non_zero_mask] = 0.0775 * np.power(intensity_map[non_zero_mask], 0.46)
        return flame_length
    
    def _calculate_heat_flux(self, intensity_map: np.ndarray, flame_length_map: np.ndarray) -> np.ndarray:
        """열 유속 계산"""
        # 간단한 열 전달 모델
        heat_flux = intensity_map * 0.3  # 복사열 비율
        
        # 화염 길이에 따른 열 전달 범위 확장
        from scipy.ndimage import gaussian_filter
        heat_spread = gaussian_filter(heat_flux, sigma=1.0)
        
        return heat_spread
    
    def _calculate_ember_production(self, intensity_map: np.ndarray, flame_length_map: np.ndarray) -> np.ndarray:
        """불씨 생성량 계산"""
        # 높은 강도와 긴 화염에서 더 많은 불씨 생성
        ember_production = intensity_map * flame_length_map * 0.001
        
        # 연료 타입별 불씨 생성 특성
        if self.fuel_map is not None:
            ember_prone_fuels = ['TL2', 'TL3', 'TU2', 'TU3', 'SB2']  # 불씨 생성이 많은 연료
            for fuel_type in ember_prone_fuels:
                fuel_mask = (self.fuel_map == fuel_type)
                ember_production[fuel_mask] *= 2.0
        
        return ember_production
    
    def _classify_fire_behavior(self, intensity_map: np.ndarray, flame_length_map: np.ndarray) -> np.ndarray:
        """화재 행동 유형 분류"""
        behavior_map = np.full(intensity_map.shape, FireBehaviorType.SURFACE.value, dtype=object)
        
        # 강도와 화염 길이에 따른 분류
        crown_mask = (intensity_map > 4000) & (flame_length_map > 3.5)  # 수관화재
        ground_mask = (intensity_map > 0) & (intensity_map < 500)       # 지중화재
        spotting_mask = (intensity_map > 2000) & (flame_length_map > 2.0)  # 비화 가능
        
        behavior_map[crown_mask] = FireBehaviorType.CROWN.value
        behavior_map[ground_mask] = FireBehaviorType.GROUND.value
        behavior_map[spotting_mask] = FireBehaviorType.SPOTTING.value
        
        # 극한 조건에서 불꽃 폭풍
        if self.weather_conditions and self.weather_conditions.wind_speed > 25:
            storm_mask = (intensity_map > 8000) & (flame_length_map > 5.0)
            behavior_map[storm_mask] = FireBehaviorType.EMBER_STORM.value
        
        return behavior_map
    
    def _calculate_spotting_probability(self, source_i: int, source_j: int, ember_potential: float) -> float:
        """비화 확률 계산"""
        base_prob = ember_potential * 0.01
        
        if self.weather_conditions is None:
            return base_prob
        
        # 바람 효과
        wind_factor = min(self.weather_conditions.wind_speed / 30.0, 1.0)
        
        # 습도 효과 (낮은 습도일수록 높은 확률)
        humidity_factor = 1.0 - self.weather_conditions.relative_humidity / 100.0
        
        # 대기 안정도 효과
        stability_factor = 1.0
        if hasattr(self.weather_conditions, 'stability_class'):
            if self.weather_conditions.stability_class in ['A', 'B']:  # 불안정
                stability_factor = 1.5
            elif self.weather_conditions.stability_class in ['E', 'F']:  # 안정
                stability_factor = 0.5
        
        total_prob = base_prob * wind_factor * humidity_factor * stability_factor
        return min(total_prob, 0.1)  # 최대 10% 확률
    
    def _calculate_ember_trajectory(self, source_i: int, source_j: int, max_distance: float) -> List[Tuple[int, int]]:
        """불씨 궤적 계산"""
        landing_points = []
        
        if self.weather_conditions is None:
            return landing_points
        
        # 바람 방향과 속도에 따른 불씨 이동
        wind_dir_rad = np.radians(self.weather_conditions.wind_direction)
        wind_speed = self.weather_conditions.wind_speed
        
        # 여러 개의 불씨 (크기와 무게가 다름)
        num_embers = random.randint(1, 5)
        
        for _ in range(num_embers):
            # 불씨 크기에 따른 이동 거리 (작은 불씨가 더 멀리)
            ember_size_factor = random.uniform(0.5, 2.0)
            travel_distance = (wind_speed * 10 / ember_size_factor) * random.uniform(0.5, 1.5)
            travel_distance = min(travel_distance, max_distance)
            
            # 바람 방향 + 약간의 무작위성
            direction_noise = np.radians(random.uniform(-30, 30))
            actual_direction = wind_dir_rad + direction_noise
            
            # 착지점 계산
            distance_cells = travel_distance / self.cell_size
            delta_i = int(distance_cells * np.cos(actual_direction))
            delta_j = int(distance_cells * np.sin(actual_direction))
            
            land_i = source_i + delta_i
            land_j = source_j + delta_j
            
            if 0 <= land_i < self.height and 0 <= land_j < self.width:
                landing_points.append((land_i, land_j))
        
        return landing_points
    
    def _calculate_ignition_probability(self, i: int, j: int) -> float:
        """착화 확률 계산"""
        base_prob = 0.3
        
        # 연료 수분 효과
        if self.fuel_moisture_map is not None:
            moisture_factor = 1.0 - 2.0 * self.fuel_moisture_map[i, j]
            moisture_factor = np.clip(moisture_factor, 0.1, 1.0)
        else:
            moisture_factor = 1.0
        
        # 연료 타입 효과
        if self.fuel_map is not None:
            fuel_type = str(self.fuel_map[i, j])
            fuel_ignition = {
                'GS1': 0.8, 'GS2': 0.9, 'GS3': 0.95,  # 풀류 - 쉽게 착화
                'GR1': 0.9, 'GR2': 0.95,               # 건조 풀 - 매우 쉽게 착화
                'TL1': 0.4, 'TL2': 0.6, 'TL3': 0.7,    # 목재 - 중간 착화
                'TU1': 0.5, 'TU2': 0.7, 'TU3': 0.8,    # 관목 - 중간-높은 착화
                'SB1': 0.7, 'SB2': 0.8                 # 관목-풀 혼합 - 높은 착화
            }
            fuel_factor = fuel_ignition.get(fuel_type, 0.5)
        else:
            fuel_factor = 1.0
        
        total_prob = base_prob * moisture_factor * fuel_factor
        return min(total_prob, 0.95)
    
    def _get_line_cells(self, x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """두 점 사이의 선상 셀들 반환 (Bresenham 알고리즘)"""
        cells = []
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            cells.append((x1, y1))
            
            if x1 == x2 and y1 == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        
        return cells
    
    def _apply_ground_suppression(self, grid: np.ndarray, ground_crews: List[Dict]) -> np.ndarray:
        """지상 소방대 진압 효과 적용"""
        modified_grid = grid.copy()
        
        for crew in ground_crews:
            location = crew.get('location', (0, 0))
            effectiveness = crew.get('effectiveness', 0.8)
            range_radius = crew.get('range', 3)
            
            i, j = location
            
            # 진압 범위 내 화재 진압
            for di in range(-range_radius, range_radius + 1):
                for dj in range(-range_radius, range_radius + 1):
                    ni, nj = i + di, j + dj
                    if (0 <= ni < self.height and 0 <= nj < self.width and
                        modified_grid[ni, nj] == 1):  # 연소 중
                        
                        if random.random() < effectiveness:
                            modified_grid[ni, nj] = 2  # 연소됨으로 변경 (진압됨)
        
        return modified_grid
    
    def _apply_aerial_suppression(self, grid: np.ndarray, aerial_drops: List[Dict]) -> np.ndarray:
        """항공 살수 효과 적용"""
        modified_grid = grid.copy()
        
        for drop in aerial_drops:
            center = drop.get('center', (0, 0))
            radius = drop.get('radius', 5)
            effectiveness = drop.get('effectiveness', 0.9)
            
            i_center, j_center = center
            
            # 원형 영역에 진압 효과 적용
            for i in range(max(0, i_center - radius), min(self.height, i_center + radius + 1)):
                for j in range(max(0, j_center - radius), min(self.width, j_center + radius + 1)):
                    distance = np.sqrt((i - i_center)**2 + (j - j_center)**2)
                    
                    if distance <= radius and modified_grid[i, j] == 1:
                        # 거리에 따른 효과 감소
                        distance_factor = 1.0 - (distance / radius) * 0.3
                        actual_effectiveness = effectiveness * distance_factor
                        
                        if random.random() < actual_effectiveness:
                            modified_grid[i, j] = 2
        
        return modified_grid
    
    def _apply_firebreaks(self, grid: np.ndarray, firebreaks: List[Dict]) -> np.ndarray:
        """방화선 효과 적용"""
        modified_grid = grid.copy()
        
        for firebreak in firebreaks:
            start = firebreak.get('start', (0, 0))
            end = firebreak.get('end', (0, 0))
            width = firebreak.get('width', 1)
            
            # 방화선 라인 상의 셀들을 연료 없음으로 설정
            line_cells = self._get_line_cells(start[0], start[1], end[0], end[1])
            
            for i, j in line_cells:
                # 방화선 폭만큼 확장
                for di in range(-width, width + 1):
                    for dj in range(-width, width + 1):
                        ni, nj = i + di, j + dj
                        if 0 <= ni < self.height and 0 <= nj < self.width:
                            if modified_grid[ni, nj] == 1:  # 연소 중이면 진압
                                modified_grid[ni, nj] = 2
                            # 연료 맵에서도 제거 (다음 단계에서 착화 방지)
                            if self.fuel_map is not None:
                                self.fuel_map[ni, nj] = 0  # 연료 없음
        
        return modified_grid
    
    def _apply_retardant(self, grid: np.ndarray, retardant_drops: List[Dict]) -> np.ndarray:
        """화재진압제 효과 적용"""
        modified_grid = grid.copy()
        
        for drop in retardant_drops:
            area = drop.get('area', [])  # 좌표 리스트
            effectiveness = drop.get('effectiveness', 0.95)
            duration = drop.get('duration', 10)  # 효과 지속 시간
            
            for i, j in area:
                if (0 <= i < self.height and 0 <= j < self.width and
                    modified_grid[i, j] == 1):
                    
                    if random.random() < effectiveness:
                        modified_grid[i, j] = 2
                        
                    # 진압제 효과로 연료 수분량 증가
                    if self.fuel_moisture_map is not None:
                        self.fuel_moisture_map[i, j] = min(0.5, self.fuel_moisture_map[i, j] + 0.2)
        
        return modified_grid
    
    def get_realism_metrics(self) -> Dict[str, Any]:
        """현실성 지표 계산"""
        metrics = {
            'spotting_events': len(self.spotting_events),
            'max_fire_intensity': float(np.max(self.fire_intensity_map)),
            'mean_flame_length': float(np.mean(self.flame_length_map[self.flame_length_map > 0])) if np.any(self.flame_length_map > 0) else 0,
            'fire_behavior_diversity': len(set(self.fire_behavior_history)),
            'suppression_effectiveness': len(self.suppression_activities)
        }
        
        # 화재 행동 분포
        if self.fire_behavior_history:
            behavior_counts = {}
            for behavior in self.fire_behavior_history:
                behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
            metrics['behavior_distribution'] = behavior_counts
        
        return metrics

# 테스트 및 사용 예시
if __name__ == "__main__":
    print("현실적 화재 모델 테스트")
    
    # 모델 초기화
    fire_model = RealisticFireModel((100, 100), cell_size=30.0)
    
    # 연료 맵 설정
    fire_model.fuel_map = np.random.choice(['TL1', 'TL2', 'GS1', 'GS2', 'TU1'], size=(100, 100))
    
    # 기상 조건 설정
    fire_model.weather_conditions = DetailedWeatherConditions(
        temperature=35.0,
        relative_humidity=25.0,
        wind_speed=15.0,
        wind_direction=270.0,
        atmospheric_pressure=1013.0,
        solar_radiation=800.0,
        precipitation=0.0,
        drought_index=0.8,
        fire_weather_index=85.0,
        stability_class='B'
    )
    
    # 연료 수분 모델 설정
    base_moisture = {'TL1': 0.12, 'TL2': 0.15, 'GS1': 0.08, 'GS2': 0.10, 'TU1': 0.14}
    fire_model.set_fuel_moisture_model(base_moisture, seasonal_factor=0.8)
    
    # 테스트 화재 그리드
    test_grid = np.zeros((100, 100), dtype=int)
    test_grid[45:55, 45:55] = 1  # 중앙에 화재
    
    # 화재 행동 계산
    behavior_data = fire_model.calculate_fire_behavior(test_grid)
    print(f"최대 화재 강도: {np.max(behavior_data['fire_intensity']):.1f} kW/m")
    print(f"최대 화염 길이: {np.max(behavior_data['flame_length']):.1f} m")
    
    # 비화 시뮬레이션
    new_ignitions = fire_model.simulate_spotting(test_grid)
    print(f"비화 착화점 수: {len(new_ignitions)}")
    
    # 계절별 효과
    seasonal_effects = fire_model.calculate_seasonal_effects(datetime.now())
    print(f"계절 위험도: {seasonal_effects['seasonal_risk']:.2f}")
    
    # 현실성 지표
    realism_metrics = fire_model.get_realism_metrics()
    print(f"현실성 지표: {realism_metrics}")
    
    print("현실적 화재 모델링 완료!")
