"""
지형 효과 모델링 모듈
경사도, 사면 방향, 고도 등이 화재 확산에 미치는 영향 계산
"""

import numpy as np
import rasterio
from scipy import ndimage
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

class TerrainModel:
    """지형 효과 모델링"""
    
    def __init__(self, dem_path=None, resolution=30):
        """
        dem_path: DEM 파일 경로 (GeoTIFF)
        resolution: 격자 해상도 (미터)
        """
        self.dem_path = dem_path
        self.resolution = resolution
        self.elevation = None
        self.slope = None
        self.aspect = None
        
        if dem_path:
            self.load_dem(dem_path)
    
    def load_dem(self, dem_path):
        """DEM 데이터 로드"""
        try:
            with rasterio.open(dem_path) as dataset:
                self.elevation = dataset.read(1)
                self.transform = dataset.transform
                self.crs = dataset.crs
                
            print(f"DEM 로드 완료: {self.elevation.shape}")
            self.calculate_terrain_derivatives()
            
        except Exception as e:
            print(f"DEM 로드 실패: {e}")
            # 가상 DEM 생성
            self.create_synthetic_dem()
    
    def create_synthetic_dem(self, shape=(100, 100)):
        """가상 DEM 생성 (테스트용)"""
        x = np.linspace(0, 10, shape[1])
        y = np.linspace(0, 10, shape[0])
        X, Y = np.meshgrid(x, y)
        
        # 복잡한 지형 생성 (여러 산봉우리와 계곡)
        self.elevation = (
            100 * np.sin(X) * np.cos(Y) +
            50 * np.sin(2*X) * np.sin(2*Y) +
            200 * np.exp(-((X-5)**2 + (Y-5)**2)/4) +
            np.random.normal(0, 5, shape)  # 노이즈 추가
        )
        self.elevation = np.maximum(self.elevation, 0)  # 음수 고도 제거
        
        print(f"가상 DEM 생성: {self.elevation.shape}")
        self.calculate_terrain_derivatives()
    
    def calculate_terrain_derivatives(self):
        """경사도와 사면 방향 계산"""
        if self.elevation is None:
            return
            
        # 경사도 계산 (gradient magnitude)
        gy, gx = np.gradient(self.elevation, self.resolution)
        self.slope = np.degrees(np.arctan(np.sqrt(gx**2 + gy**2)))
        
        # 사면 방향 계산 (aspect, 북쪽=0도, 시계방향)
        self.aspect = np.degrees(np.arctan2(-gx, gy))
        self.aspect = (self.aspect + 360) % 360  # 0-360도 범위로 정규화
        
        print(f"지형 특성 계산 완료")
        print(f"  경사도 범위: {self.slope.min():.1f}° - {self.slope.max():.1f}°")
        print(f"  평균 경사도: {self.slope.mean():.1f}°")
    
    def get_slope_effect(self, from_x, from_y, to_x, to_y):
        """경사도가 화재 확산에 미치는 영향"""
        if self.slope is None:
            return 1.0
            
        # 확산 방향의 경사도
        try:
            slope_from = self.slope[from_x, from_y]
            slope_to = self.slope[to_x, to_y]
            avg_slope = (slope_from + slope_to) / 2
            
            # 고도차 계산
            elev_diff = self.elevation[to_x, to_y] - self.elevation[from_x, from_y]
            
            # 상향 확산 vs 하향 확산
            if elev_diff > 0:  # 상향 확산 (더 빠름)
                slope_factor = 1.0 + (avg_slope / 45.0) * 0.5  # 최대 50% 증가
            else:  # 하향 확산 (조금 느림)
                slope_factor = 1.0 - (avg_slope / 90.0) * 0.2  # 최대 20% 감소
                
            return max(0.1, slope_factor)
            
        except IndexError:
            return 1.0
    
    def get_aspect_effect(self, from_x, from_y, to_x, to_y, wind_direction=None):
        """사면 방향과 풍향의 상호작용 효과"""
        if self.aspect is None:
            return 1.0
            
        try:
            aspect_from = self.aspect[from_x, from_y]
            aspect_to = self.aspect[to_x, to_y]
            avg_aspect = (aspect_from + aspect_to) / 2
            
            if wind_direction is None:
                wind_direction = 180  # 기본값: 남풍
                
            # 사면이 바람을 받는 정도
            aspect_diff = abs(avg_aspect - wind_direction)
            if aspect_diff > 180:
                aspect_diff = 360 - aspect_diff
                
            # 풍향과 일치하는 사면일수록 건조 효과 증가
            if aspect_diff <= 45:  # 바람받이 사면
                aspect_factor = 1.2
            elif aspect_diff >= 135:  # 바람그늘 사면
                aspect_factor = 0.9
            else:  # 측면
                aspect_factor = 1.0
                
            return aspect_factor
            
        except IndexError:
            return 1.0
    
    def get_elevation_effect(self, x, y):
        """고도가 화재 확산에 미치는 영향"""
        if self.elevation is None:
            return 1.0
            
        try:
            elevation = self.elevation[x, y]
            
            # 고도별 효과 (높을수록 건조, 바람 강함)
            if elevation > 1000:
                return 1.3
            elif elevation > 500:
                return 1.1
            elif elevation > 200:
                return 1.0
            else:
                return 0.9
                
        except IndexError:
            return 1.0
    
    def calculate_fire_spread_coefficient(self, from_x, from_y, to_x, to_y, 
                                        wind_direction=None, weather_factor=1.0):
        """종합적인 지형 기반 확산 계수 계산"""
        slope_effect = self.get_slope_effect(from_x, from_y, to_x, to_y)
        aspect_effect = self.get_aspect_effect(from_x, from_y, to_x, to_y, wind_direction)
        elevation_effect = self.get_elevation_effect(to_x, to_y)
        
        # 종합 계수 계산
        terrain_coefficient = slope_effect * aspect_effect * elevation_effect * weather_factor
        
        return min(terrain_coefficient, 3.0)  # 최대 3배까지 증가 제한
    
    def create_fire_hazard_map(self, wind_direction=180):
        """지형 기반 화재 위험도 맵 생성"""
        if self.elevation is None:
            return None
            
        hazard_map = np.ones_like(self.elevation)
        
        for i in range(1, self.elevation.shape[0]-1):
            for j in range(1, self.elevation.shape[1]-1):
                # 8방향 확산 계수의 평균
                coeffs = []
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        coeff = self.calculate_fire_spread_coefficient(
                            i, j, i+di, j+dj, wind_direction
                        )
                        coeffs.append(coeff)
                
                hazard_map[i, j] = np.mean(coeffs)
        
        return hazard_map
    
    def visualize_terrain(self, save_path=None):
        """지형 특성 시각화"""
        if self.elevation is None:
            print("지형 데이터가 없습니다.")
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 고도
        im1 = axes[0,0].imshow(self.elevation, cmap='terrain')
        axes[0,0].set_title('고도 (m)')
        axes[0,0].axis('off')
        plt.colorbar(im1, ax=axes[0,0])
        
        # 경사도
        im2 = axes[0,1].imshow(self.slope, cmap='Reds')
        axes[0,1].set_title('경사도 (도)')
        axes[0,1].axis('off')
        plt.colorbar(im2, ax=axes[0,1])
        
        # 사면 방향
        im3 = axes[1,0].imshow(self.aspect, cmap='hsv')
        axes[1,0].set_title('사면 방향 (도)')
        axes[1,0].axis('off')
        plt.colorbar(im3, ax=axes[1,0])
        
        # 화재 위험도 (남풍 기준)
        hazard_map = self.create_fire_hazard_map(wind_direction=180)
        im4 = axes[1,1].imshow(hazard_map, cmap='YlOrRd')
        axes[1,1].set_title('화재 위험도 (남풍시)')
        axes[1,1].axis('off')
        plt.colorbar(im4, ax=axes[1,1])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def export_terrain_data(self, output_path):
        """지형 데이터 내보내기"""
        if self.elevation is None:
            print("지형 데이터가 없습니다.")
            return
            
        np.savez_compressed(output_path,
                          elevation=self.elevation,
                          slope=self.slope,
                          aspect=self.aspect,
                          resolution=self.resolution)
        
        print(f"지형 데이터 저장: {output_path}")

class TopographicFireModel:
    """지형 기반 화재 확산 모델"""
    
    def __init__(self, terrain_model, base_spread_prob=0.2):
        self.terrain_model = terrain_model
        self.base_spread_prob = base_spread_prob
    
    def get_adjusted_spread_probability(self, from_x, from_y, to_x, to_y, 
                                      wind_direction=None, weather_factor=1.0):
        """지형 조건을 반영한 조정된 확산 확률"""
        terrain_coeff = self.terrain_model.calculate_fire_spread_coefficient(
            from_x, from_y, to_x, to_y, wind_direction, weather_factor
        )
        
        adjusted_prob = self.base_spread_prob * terrain_coeff
        return min(adjusted_prob, 1.0)  # 확률은 1을 넘을 수 없음
    
    def create_probability_matrix(self, center_x, center_y, radius=10, 
                                wind_direction=180, weather_factor=1.0):
        """특정 지점 주변의 확산 확률 매트릭스 생성"""
        size = 2 * radius + 1
        prob_matrix = np.zeros((size, size))
        
        for i in range(size):
            for j in range(size):
                to_x = center_x - radius + i
                to_y = center_y - radius + j
                
                if (0 <= to_x < self.terrain_model.elevation.shape[0] and 
                    0 <= to_y < self.terrain_model.elevation.shape[1]):
                    
                    prob = self.get_adjusted_spread_probability(
                        center_x, center_y, to_x, to_y, 
                        wind_direction, weather_factor
                    )
                    prob_matrix[i, j] = prob
        
        return prob_matrix

# 사용 예시
if __name__ == '__main__':
    # 지형 모델 생성 (가상 DEM 사용)
    terrain_model = TerrainModel()
    
    # 지형 특성 시각화
    terrain_model.visualize_terrain('terrain_analysis.png')
    
    # 화재 확산 모델 생성
    fire_model = TopographicFireModel(terrain_model)
    
    # 특정 지점에서의 확산 확률 매트릭스
    center_x, center_y = 50, 50
    prob_matrix = fire_model.create_probability_matrix(
        center_x, center_y, radius=15, wind_direction=225  # 서남풍
    )
    
    # 확산 확률 시각화
    plt.figure(figsize=(8, 6))
    plt.imshow(prob_matrix, cmap='Reds', interpolation='nearest')
    plt.title(f'지형 조건을 반영한 화재 확산 확률\n중심점: ({center_x}, {center_y})')
    plt.colorbar(label='확산 확률')
    plt.axis('off')
    plt.show()
    
    print(f"최대 확산 확률: {prob_matrix.max():.3f}")
    print(f"평균 확산 확률: {prob_matrix.mean():.3f}")
