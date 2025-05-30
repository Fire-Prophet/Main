# fire_model.py
# 산불 확산 모델 (셀룰러 오토마타 기반 예시)
import numpy as np

class FireSimulation:
    def __init__(self, environment, ignition_points):
        self.env = environment
        self.grid = np.zeros(self.env.shape, dtype=int)  # 0: 미연소, 1: 연소중, 2: 연소 후
        for y, x in ignition_points:
            self.grid[y, x] = 1
        self.step_count = 0

    def step(self):
        new_grid = self.grid.copy()
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                if self.grid[y, x] == 1:
                    new_grid[y, x] = 2  # 연소 후
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.grid.shape[0] and 0 <= nx < self.grid.shape[1]:
                                if self.grid[ny, nx] == 0 and self.env.can_burn(ny, nx):
                                    if self.env.spread_probability(y, x, ny, nx) > np.random.rand():
                                        new_grid[ny, nx] = 1
        self.grid = new_grid
        self.step_count += 1

    def is_extinguished(self):
        return np.all((self.grid == 0) | (self.grid == 2))
