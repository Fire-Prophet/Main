"""
고급 CA 화재 모델
Moore 이웃, 확률적 소화, 다중 점화, 현실적 규칙 구현
"""

import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import json
from typing import List, Tuple, Optional, Dict

class AdvancedCAModel:
    """고급 셀룰러 오토마타 화재 모델"""
    
    # 상태 정의
    EMPTY = 0       # 빈 공간
    TREE = 1        # 나무/연료
    BURNING = 2     # 연소중
    BURNED = 3      # 연소 완료
    WET = 4         # 습한 상태 (소화)
    
    def __init__(self, grid_shape: Tuple[int, int], 
                 neighborhood='moore',  # 'moore' or 'von_neumann'
                 seed: Optional[int] = None):
        """
        grid_shape: 격자 크기 (height, width)
        neighborhood: 이웃 정의 방식
        seed: 랜덤 시드
        """
        self.grid_shape = grid_shape
        self.height, self.width = grid_shape  # Add height and width attributes for compatibility
        self.neighborhood = neighborhood
        self.rng = np.random.default_rng(seed)
        
        # 격자 및 상태
        self.grid = np.zeros(grid_shape, dtype=int)
        self.fuel_map = None
        self.terrain_model = None
        self.weather_model = None
        
        # 시뮬레이션 설정
        self.step_count = 0
        self.history = []
        self.fire_sources = []  # 다중 점화점
        
        # 모델 파라미터
        self.params = {
            'base_spread_prob': 0.15,
            'ignition_prob': 0.001,
            'extinguish_prob': 0.05,
            'fuel_consumption_time': 3,  # 연소 지속 시간
            'moisture_recovery_time': 10,  # 습도 회복 시간
            'firebreak_width': 2,  # 방화선 폭
        }
        
        # 연료별 특성
        self.fuel_properties = {
            'TL1': {'spread_prob': 0.10, 'burn_time': 2, 'heat_output': 1.0},
            'TL2': {'spread_prob': 0.12, 'burn_time': 3, 'heat_output': 1.1},
            'TL3': {'spread_prob': 0.13, 'burn_time': 3, 'heat_output': 1.2},
            'TU1': {'spread_prob': 0.18, 'burn_time': 4, 'heat_output': 1.5},
            'TU2': {'spread_prob': 0.20, 'burn_time': 4, 'heat_output': 1.6},
            'TU3': {'spread_prob': 0.22, 'burn_time': 5, 'heat_output': 1.7},
            'TU4': {'spread_prob': 0.20, 'burn_time': 4, 'heat_output': 1.6},
            'TU5': {'spread_prob': 0.25, 'burn_time': 5, 'heat_output': 1.8},
            'GS1': {'spread_prob': 0.30, 'burn_time': 1, 'heat_output': 0.8},
            'GR1': {'spread_prob': 0.35, 'burn_time': 1, 'heat_output': 0.6},
            'SH1': {'spread_prob': 0.28, 'burn_time': 2, 'heat_output': 0.9},
            'NB1': {'spread_prob': 0.01, 'burn_time': 0, 'heat_output': 0.1},
        }
        
        # 추가 상태 정보 저장용
        self.burn_timer = np.zeros(grid_shape, dtype=int)  # 연소 시간
        self.moisture_timer = np.zeros(grid_shape, dtype=int)  # 습도 회복 시간
        self.heat_map = np.zeros(grid_shape, dtype=float)  # 열 분포
        
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """이웃 셀 좌표 반환"""
        neighbors = []
        
        if self.neighborhood == 'moore':
            # Moore 이웃 (8방향)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
            
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_shape[0] and 0 <= ny < self.grid_shape[1]:
                        neighbors.append((nx, ny))
        
        elif self.neighborhood == 'von_neumann':
            # Von Neumann 이웃 (4방향)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_shape[0] and 0 <= ny < self.grid_shape[1]:
                    neighbors.append((nx, ny))
        
        return neighbors
    
    def get_spread_probability(self, from_x: int, from_y: int, 
                             to_x: int, to_y: int) -> float:
        """확산 확률 계산 (연료, 지형, 기상 조건 반영)"""
        base_prob = self.params['base_spread_prob']
        
        # 연료 타입별 확률
        if self.fuel_map is not None:
            fuel_type = self.fuel_map[to_x, to_y]
            if fuel_type in self.fuel_properties:
                base_prob = self.fuel_properties[fuel_type]['spread_prob']
        
        # 지형 효과
        terrain_factor = 1.0
        if self.terrain_model is not None:
            terrain_factor = self.terrain_model.calculate_fire_spread_coefficient(
                from_x, from_y, to_x, to_y
            )
        
        # 기상 효과
        weather_factor = 1.0
        if self.weather_model is not None:
            wind_effect = self.weather_model.get_wind_effect(
                from_x, from_y, to_x, to_y
            )
            humidity_effect = self.weather_model.get_humidity_effect()
            weather_factor = wind_effect * humidity_effect
        
        # 열 확산 효과
        heat_effect = 1.0 + (self.heat_map[from_x, from_y] * 0.1)
        
        # 거리 효과 (대각선 이웃은 확률 감소)
        distance_factor = 1.0
        if abs(to_x - from_x) + abs(to_y - from_y) == 2:  # 대각선
            distance_factor = 0.7
        
        final_prob = (base_prob * terrain_factor * weather_factor * 
                        heat_effect * distance_factor)
        
        return min(final_prob, 1.0)
    
    def initialize(self, tree_density: float = 0.7, 
                 firebreaks: Optional[List[Dict]] = None):
        """격자 초기화"""
        # 기본 나무 분포
        self.grid = (self.rng.random(self.grid_shape) < tree_density).astype(int)
        
        # 방화선 설정
        if firebreaks:
            for firebreak in firebreaks:
                self.create_firebreak(**firebreak)
        
        # 상태 초기화
        self.burn_timer.fill(0)
        self.moisture_timer.fill(0)
        self.heat_map.fill(0)
        self.step_count = 0
        self.history = []
        
    def create_firebreak(self, start: Tuple[int, int], end: Tuple[int, int], 
                        width: int = 2):
        """방화선 생성"""
        x1, y1 = start
        x2, y2 = end
        
        # 직선 방화선 생성
        length = max(abs(x2 - x1), abs(y2 - y1))
        for i in range(length + 1):
            t = i / max(length, 1)
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            
            # 폭만큼 확장
            for dx in range(-width//2, width//2 + 1):
                for dy in range(-width//2, width//2 + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_shape[0] and 0 <= ny < self.grid_shape[1]:
                        self.grid[nx, ny] = self.EMPTY
    
    def add_ignition_point(self, x: int, y: int, intensity: float = 1.0):
        """점화점 추가"""
        if 0 <= x < self.grid_shape[0] and 0 <= y < self.grid_shape[1]:
            self.grid[x, y] = self.BURNING
            self.heat_map[x, y] = intensity
            self.fire_sources.append((x, y, intensity, self.step_count))
    
    def apply_suppression(self, center: Tuple[int, int], radius: int = 3,
                        effectiveness: float = 0.8):
        """소화 활동 적용"""
        x_center, y_center = center
        
        for x in range(max(0, x_center - radius), 
                       min(self.grid_shape[0], x_center + radius + 1)):
            for y in range(max(0, y_center - radius),
                         min(self.grid_shape[1], y_center + radius + 1)):
                
                distance = np.sqrt((x - x_center)**2 + (y - y_center)**2)
                if distance <= radius:
                    # 거리에 따른 소화 효과 감소
                    suppression_prob = effectiveness * (1 - distance / radius)
                    
                    if self.rng.random() < suppression_prob:
                        if self.grid[x, y] == self.BURNING:
                            self.grid[x, y] = self.WET
                            self.moisture_timer[x, y] = self.params['moisture_recovery_time']
                        elif self.grid[x, y] == self.TREE:
                            self.grid[x, y] = self.WET
                            self.moisture_timer[x, y] = self.params['moisture_recovery_time']
    
    def step(self):
        """시뮬레이션 한 스텝 실행"""
        new_grid = self.grid.copy()
        new_heat_map = self.heat_map.copy()
        
        # 1. 연소 중인 셀들의 확산
        burning_cells = np.where(self.grid == self.BURNING)
        
        for i, j in zip(burning_cells[0], burning_cells[1]):
            # 주변으로 화재 확산
            neighbors = self.get_neighbors(i, j)
            
            for ni, nj in neighbors:
                if self.grid[ni, nj] == self.TREE:
                    spread_prob = self.get_spread_probability(i, j, ni, nj)
                    if self.rng.random() < spread_prob:
                        new_grid[ni, nj] = self.BURNING
                        
                        # 연료별 열 출력
                        heat_output = 1.0
                        if self.fuel_map is not None:
                            fuel_type = self.fuel_map[ni, nj]
                            if fuel_type in self.fuel_properties:
                                heat_output = self.fuel_properties[fuel_type]['heat_output']
                        
                        new_heat_map[ni, nj] = heat_output
            
            # 연소 시간 증가
            self.burn_timer[i, j] += 1
            
            # 연소 완료 체크
            burn_duration = self.params['fuel_consumption_time']
            if self.fuel_map is not None:
                fuel_type = self.fuel_map[i, j]
                if fuel_type in self.fuel_properties:
                    burn_duration = self.fuel_properties[fuel_type]['burn_time']
            
            if self.burn_timer[i, j] >= burn_duration:
                new_grid[i, j] = self.BURNED
                new_heat_map[i, j] = 0
        
        # 2. 확률적 소화 (자연 소화)
        extinguish_mask = (
            (self.grid == self.BURNING) & 
            (self.rng.random(self.grid_shape) < self.params['extinguish_prob'])
        )
        new_grid[extinguish_mask] = self.BURNED
        new_heat_map[extinguish_mask] = 0
        
        # 3. 습도 회복
        wet_cells = np.where(self.grid == self.WET)
        for i, j in zip(wet_cells[0], wet_cells[1]):
            self.moisture_timer[i, j] -= 1
            if self.moisture_timer[i, j] <= 0:
                new_grid[i, j] = self.TREE
        
        # 4. 열 확산 및 냉각
        new_heat_map = ndimage.gaussian_filter(new_heat_map, sigma=0.5)
        new_heat_map *= 0.9  # 냉각 효과
        
        # 5. 자연 발화
        spontaneous_ignition = (
            (self.grid == self.TREE) & 
            (self.rng.random(self.grid_shape) < self.params['ignition_prob'])
        )
        new_grid[spontaneous_ignition] = self.BURNING
        
        # 상태 업데이트
        self.grid = new_grid
        self.heat_map = new_heat_map
        self.step_count += 1
        
        # 통계 기록
        stats = self.calculate_statistics()
        self.history.append(stats)
        
        return stats
    
    def _apply_fire_rules(self, input_grid: np.ndarray) -> np.ndarray:
        """주어진 격자에 화재 규칙 적용 (호환성 메서드)"""
        # 현재 상태 저장
        old_grid = self.grid.copy()
        
        # 입력 격자 설정
        self.grid = input_grid.copy()
        
        # 한 스텝 적용
        self.step()
        
        # 결과 가져오기 및 상태 복원
        result = self.grid.copy()
        self.grid = old_grid
        
        return result

    def calculate_statistics(self) -> Dict:
        """현재 상태 통계 계산"""
        total_cells = self.grid.size
        
        stats = {
            'step': self.step_count,
            'empty_cells': np.sum(self.grid == self.EMPTY),
            'tree_cells': np.sum(self.grid == self.TREE),
            'burning_cells': np.sum(self.grid == self.BURNING),
            'burned_cells': np.sum(self.grid == self.BURNED),
            'wet_cells': np.sum(self.grid == self.WET),
            'total_heat': np.sum(self.heat_map),
            'max_heat': np.max(self.heat_map),
            'fire_perimeter': self._calculate_fire_perimeter(),
            'burn_ratio': np.sum(self.grid == self.BURNED) / total_cells
        }
        
        return stats
    
    def _calculate_fire_perimeter(self) -> int:
        """화재 경계선 길이 계산"""
        burning_mask = (self.grid == self.BURNING)
        eroded = ndimage.binary_erosion(burning_mask)
        perimeter = burning_mask.astype(int) - eroded.astype(int)
        return np.sum(perimeter)
    
    def is_simulation_complete(self) -> bool:
        """시뮬레이션 완료 여부 확인"""
        return np.sum(self.grid == self.BURNING) == 0
    
    def visualize(self, show_heat: bool = False, save_path: Optional[str] = None):
        """현재 상태 시각화"""
        if show_heat:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        else:
            fig, ax1 = plt.subplots(figsize=(8, 6))
        
        # 상태 색상 맵
        colors = ['white', 'green', 'red', 'black', 'blue']
        cmap = plt.matplotlib.colors.ListedColormap(colors)
        
        im1 = ax1.imshow(self.grid, cmap=cmap, vmin=0, vmax=4)
        ax1.set_title(f'화재 시뮬레이션 - Step {self.step_count}')
        ax1.axis('off')
        
        # 범례
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor='white', edgecolor='black', label='빈공간'),
            plt.Rectangle((0,0),1,1, facecolor='green', label='나무'),
            plt.Rectangle((0,0),1,1, facecolor='red', label='화재'),
            plt.Rectangle((0,0),1,1, facecolor='black', label='연소후'),
            plt.Rectangle((0,0),1,1, facecolor='blue', label='습함')
        ]
        ax1.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        
        if show_heat:
            im2 = ax2.imshow(self.heat_map, cmap='hot')
            ax2.set_title('열 분포')
            ax2.axis('off')
            plt.colorbar(im2, ax=ax2)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def save_state(self, filepath: str):
        """현재 상태 저장"""
        state_data = {
            'step_count': self.step_count,
            'grid': self.grid.tolist(),
            'heat_map': self.heat_map.tolist(),
            'burn_timer': self.burn_timer.tolist(),
            'moisture_timer': self.moisture_timer.tolist(),
            'fire_sources': self.fire_sources,
            'history': self.history,
            'params': self.params
        }
        
        with open(filepath, 'w') as f:
            json.dump(state_data, f)
    
    def load_state(self, filepath: str):
        """상태 로드"""
        with open(filepath, 'r') as f:
            state_data = json.load(f)
        
        self.step_count = state_data['step_count']
        self.grid = np.array(state_data['grid'])
        self.heat_map = np.array(state_data['heat_map'])
        self.burn_timer = np.array(state_data['burn_timer'])
        self.moisture_timer = np.array(state_data['moisture_timer'])
        self.fire_sources = state_data['fire_sources']
        self.history = state_data['history']
        self.params.update(state_data['params'])

# 사용 예시
if __name__ == '__main__':
    # 고급 CA 모델 생성
    ca_model = AdvancedCAModel(
        grid_shape=(100, 100),
        neighborhood='moore',
        seed=42
    )
    
    # 방화선 설정
    firebreaks = [
        {'start': (10, 0), 'end': (10, 99), 'width': 3},    # 수직 방화선
        {'start': (0, 50), 'end': (99, 50), 'width': 2},    # 수평 방화선
    ]
    
    # 초기화
    ca_model.initialize(tree_density=0.8, firebreaks=firebreaks)
    
    # 다중 점화
    ca_model.add_ignition_point(25, 25, intensity=1.5)
    ca_model.add_ignition_point(75, 75, intensity=1.2)
    
    # 시뮬레이션 실행
    for step in range(50):
        stats = ca_model.step()
        
        # 중간에 소화 활동 적용
        if step == 20:
            ca_model.apply_suppression((30, 30), radius=5, effectiveness=0.9)
        
        # 주기적 시각화
        if step % 10 == 0:
            ca_model.visualize(show_heat=True)
        
        # 시뮬레이션 완료 체크
        if ca_model.is_simulation_complete():
            print(f"시뮬레이션 완료: {step} 스텝")
            break
    
    # 최종 상태 저장
    ca_model.save_state('advanced_ca_simulation.json')
    
    print("고급 CA 시뮬레이션 완료!")

# Backward compatibility alias
AdvancedCAFireModel = AdvancedCAModel

# This is an additional comment to create a new commit.
