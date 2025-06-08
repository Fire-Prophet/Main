\
# filepath: /Users/mac/Git/fire_simulation/model/fuel_models.py
from dataclasses import dataclass

@dataclass
class AndersonFuelModel:
    """앤더슨 13 연료 모델 데이터 클래스"""
    model_id: int
    name: str
    fuel_load_1h: float  # 1시간 연료 하중 (tons/acre)
    fuel_load_10h: float  # 10시간 연료 하중
    fuel_load_100h: float  # 100시간 연료 하중
    sav_1h: float  # 표면적-부피비 (1/ft)
    sav_10h: float
    sav_100h: float
    fuel_bed_depth: float  # 연료층 깊이 (ft)
    extinction_moisture: float  # 소화 습도 (%)
    heat_content: float  # 열 함량 (BTU/lb)

class AndersonFuelModels:
    """앤더슨 13 연료 모델 정의"""
    
    MODELS = {
        1: AndersonFuelModel(1, "Short Grass", 0.74, 0.0, 0.0, 3500, 0, 0, 1.0, 12, 8000),
        2: AndersonFuelModel(2, "Timber Grass", 2.0, 1.0, 0.5, 3000, 109, 30, 1.0, 15, 8000),
        3: AndersonFuelModel(3, "Tall Grass", 3.01, 0.0, 0.0, 1500, 0, 0, 2.5, 25, 8000),
        4: AndersonFuelModel(4, "Chaparral", 5.01, 4.01, 2.0, 2000, 109, 30, 6.0, 20, 8000),
        5: AndersonFuelModel(5, "Brush", 1.0, 0.5, 0.0, 2000, 109, 0, 2.0, 20, 8000),
        6: AndersonFuelModel(6, "Dormant Brush", 1.5, 2.5, 2.0, 1750, 109, 30, 2.5, 25, 8000),
        7: AndersonFuelModel(7, "Southern Rough", 1.13, 1.87, 1.5, 1750, 109, 30, 2.5, 40, 8000),
        8: AndersonFuelModel(8, "Closed Timber Litter", 1.5, 1.0, 2.5, 2000, 109, 30, 0.2, 30, 8000),
        9: AndersonFuelModel(9, "Hardwood Litter", 2.92, 0.41, 0.15, 2500, 109, 30, 0.2, 25, 8000),
        10: AndersonFuelModel(10, "Timber Litter", 3.01, 2.0, 5.01, 2000, 109, 30, 1.0, 25, 8000),
        11: AndersonFuelModel(11, "Light Slash", 1.5, 4.51, 5.51, 1500, 109, 30, 1.0, 15, 8000),
        12: AndersonFuelModel(12, "Medium Slash", 4.01, 14.03, 16.53, 1500, 109, 30, 2.3, 20, 8000),
        13: AndersonFuelModel(13, "Heavy Slash", 7.01, 23.04, 28.05, 1500, 109, 30, 3.0, 25, 8000),
    }
