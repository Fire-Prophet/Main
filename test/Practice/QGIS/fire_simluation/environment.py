# environment.py
# 환경 정보 및 확산 조건 처리
import numpy as np

class Environment:
    def __init__(self, dem_path, wind_speed, wind_dir, humidity):
        self.shape = (100, 100)  # 예시: 100x100 그리드
        self.dem = np.zeros(self.shape)  # 실제 DEM 데이터로 대체 가능
        self.wind_speed = wind_speed
        self.wind_dir = wind_dir
        self.humidity = humidity

    def can_burn(self, y, x):
        # 예시: 모든 셀은 연소 가능, 실제로는 토지피복 등 고려
        return True

    def spread_probability(self, y1, x1, y2, x2):
        # 바람, 경사, 습도 등 반영한 확산 확률 계산 (간단 예시)
        prob = 0.3 + 0.1 * self.wind_speed - 0.01 * self.humidity
        prob = np.clip(prob, 0, 1)
        return prob
