"""
기상 데이터 연동 모듈
실시간 기상 데이터 수집 및 화재 확산에 미치는 영향 모델링
"""

import numpy as np
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

class WeatherModel:
    """기상 데이터 관리 및 화재 확산 영향 계산"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.weather_data = {}
        
        # 기본 기상 조건 (API 없을 때 사용)
        self.default_weather = {
            'temperature': 25.0,      # 온도 (°C)
            'humidity': 50.0,         # 상대습도 (%)
            'wind_speed': 3.0,        # 풍속 (m/s)
            'wind_direction': 180.0,  # 풍향 (도, 북쪽=0)
            'pressure': 1013.25,      # 기압 (hPa)
            'rainfall': 0.0           # 강수량 (mm)
        }
        
    def fetch_weather_data(self, lat, lon, service='openweather'):
        """실시간 기상 데이터 수집"""
        if service == 'openweather' and self.api_key:
            return self._fetch_openweather(lat, lon)
        elif service == 'kma':
            return self._fetch_kma_data(lat, lon)
        else:
            print("기본 기상 조건 사용")
            return self.default_weather.copy()
    
    def _fetch_openweather(self, lat, lon):
        """OpenWeatherMap API 호출"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            weather = {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 180),
                'pressure': data['main']['pressure'],
                'rainfall': data.get('rain', {}).get('1h', 0.0)
            }
            
            self.weather_data = weather
            return weather
            
        except Exception as e:
            print(f"기상 데이터 수집 실패: {e}")
            return self.default_weather.copy()
    
    def _fetch_kma_data(self, lat, lon):
        """기상청 API 호출 (예시 구조)"""
        # 실제 기상청 API 연동 시 구현
        # 현재는 기본값 반환
        return self.default_weather.copy()
    
    def calculate_fire_danger_index(self, weather=None):
        """화재위험지수 계산 (FFMC, DMC 등 기반)"""
        if weather is None:
            weather = self.weather_data or self.default_weather
            
        temp = weather['temperature']
        humidity = weather['humidity']
        wind_speed = weather['wind_speed']
        rainfall = weather['rainfall']
        
        # 간단한 화재위험지수 (0-100)
        # 실제로는 Canadian Fire Weather Index 등 복잡한 모델 사용
        danger_index = 0
        
        # 온도 영향 (높을수록 위험)
        if temp > 30:
            danger_index += 30
        elif temp > 20:
            danger_index += 20
        elif temp > 10:
            danger_index += 10
            
        # 습도 영향 (낮을수록 위험)
        if humidity < 30:
            danger_index += 25
        elif humidity < 50:
            danger_index += 15
        elif humidity < 70:
            danger_index += 5
            
        # 풍속 영향 (높을수록 위험)
        danger_index += min(wind_speed * 3, 20)
        
        # 강수량 영향 (높을수록 안전)
        danger_index = max(0, danger_index - rainfall * 10)
        
        return min(danger_index, 100)
    
    def get_wind_effect(self, from_x, from_y, to_x, to_y, weather=None):
        """풍향/풍속이 화재 확산에 미치는 영향 계산"""
        if weather is None:
            weather = self.weather_data or self.default_weather
            
        wind_speed = weather['wind_speed']
        wind_direction = weather['wind_direction']
        
        # 확산 방향 계산 (북쪽=0도, 시계방향)
        spread_dx = to_x - from_x
        spread_dy = to_y - from_y
        
        if spread_dx == 0 and spread_dy == 0:
            return 1.0
            
        # 확산 방향각 계산
        spread_angle = np.degrees(np.arctan2(spread_dx, -spread_dy))
        if spread_angle < 0:
            spread_angle += 360
            
        # 풍향과 확산 방향의 차이
        angle_diff = abs(wind_direction - spread_angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
            
        # 바람 효과 계산 (순풍일 때 최대, 역풍일 때 최소)
        wind_factor = 1.0
        if angle_diff <= 45:  # 순풍
            wind_factor = 1.0 + (wind_speed * 0.1)
        elif angle_diff >= 135:  # 역풍
            wind_factor = max(0.5, 1.0 - (wind_speed * 0.05))
        else:  # 측풍
            wind_factor = 1.0 + (wind_speed * 0.02)
            
        return wind_factor
    
    def get_humidity_effect(self, weather=None):
        """습도가 연료의 연소성에 미치는 영향"""
        if weather is None:
            weather = self.weather_data or self.default_weather
            
        humidity = weather['humidity']
        
        # 습도별 연소성 계수
        if humidity > 80:
            return 0.3  # 매우 습함 - 연소 어려움
        elif humidity > 60:
            return 0.6  # 습함
        elif humidity > 40:
            return 0.8  # 보통
        elif humidity > 20:
            return 1.0  # 건조
        else:
            return 1.3  # 매우 건조 - 연소 쉬움

class TemporalModel:
    """시간/계절 요소 모델링"""
    
    def __init__(self):
        self.season_factors = {
            'spring': 1.2,  # 봄 - 건조한 낙엽
            'summer': 0.8,  # 여름 - 습도 높음
            'autumn': 1.5,  # 가을 - 낙엽, 건조
            'winter': 0.5   # 겨울 - 습도, 낮은 온도
        }
        
        self.time_factors = {
            'dawn': 0.7,      # 새벽 (5-7시)
            'morning': 0.9,   # 오전 (7-12시)
            'afternoon': 1.3, # 오후 (12-18시) - 최고온도
            'evening': 1.0,   # 저녁 (18-22시)
            'night': 0.6      # 밤 (22-5시)
        }
    
    def get_season(self, date=None):
        """현재 계절 판단"""
        if date is None:
            date = datetime.now()
            
        month = date.month
        
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'autumn'
        else:
            return 'winter'
    
    def get_time_period(self, time=None):
        """현재 시간대 판단"""
        if time is None:
            time = datetime.now().time()
            
        hour = time.hour
        
        if 5 <= hour < 7:
            return 'dawn'
        elif 7 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def get_seasonal_factor(self, date=None):
        """계절별 화재 위험도 계수"""
        season = self.get_season(date)
        return self.season_factors[season]
    
    def get_temporal_factor(self, time=None):
        """시간대별 화재 위험도 계수"""
        period = self.get_time_period(time)
        return self.time_factors[period]

class IntegratedWeatherModel:
    """통합 기상 모델"""
    
    def __init__(self, api_key=None):
        self.weather_model = WeatherModel(api_key)
        self.temporal_model = TemporalModel()
        
    def get_comprehensive_fire_risk(self, lat=None, lon=None, date_time=None):
        """종합적인 화재 위험도 계산"""
        if date_time is None:
            date_time = datetime.now()
            
        # 기상 데이터 수집
        if lat and lon:
            weather = self.weather_model.fetch_weather_data(lat, lon)
        else:
            weather = self.weather_model.default_weather
            
        # 각종 요소별 위험도 계산
        danger_index = self.weather_model.calculate_fire_danger_index(weather)
        seasonal_factor = self.temporal_model.get_seasonal_factor(date_time.date())
        temporal_factor = self.temporal_model.get_temporal_factor(date_time.time())
        humidity_effect = self.weather_model.get_humidity_effect(weather)
        
        # 종합 위험도 (0-1 스케일)
        comprehensive_risk = (
            (danger_index / 100) * 
            seasonal_factor * 
            temporal_factor * 
            humidity_effect
        ) / 3.0  # 정규화
        
        return {
            'risk_score': min(comprehensive_risk, 1.0),
            'weather': weather,
            'danger_index': danger_index,
            'seasonal_factor': seasonal_factor,
            'temporal_factor': temporal_factor,
            'humidity_effect': humidity_effect
        }

# 사용 예시
if __name__ == '__main__':
    # 기본 사용
    weather_model = WeatherModel()
    
    # 서울 좌표로 기상 데이터 수집
    lat, lon = 37.5665, 126.9780
    weather = weather_model.fetch_weather_data(lat, lon)
    print("현재 기상 조건:", weather)
    
    # 화재 위험지수 계산
    danger_index = weather_model.calculate_fire_danger_index(weather)
    print(f"화재 위험지수: {danger_index}/100")
    
    # 통합 모델 사용
    integrated_model = IntegratedWeatherModel()
    risk_assessment = integrated_model.get_comprehensive_fire_risk(lat, lon)
    print("종합 위험도 평가:", risk_assessment)
