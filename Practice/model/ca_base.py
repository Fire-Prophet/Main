import numpy as np
import matplotlib.pyplot as plt
# 이 코드를 바탕으로 CA 실험, 확장, 시각화가 가능합니다.
# 특정 규칙, 입력 데이터, 연료맵 등과 연동
class CAModel:
    def __init__(self, grid_shape, n_states=2, p_ignite=0.01, seed=None, fuel_map=None, fuel_spread_probs=None):
        """
        grid_shape: tuple, e.g. (100, 100)
        n_states: number of cell states (e.g. 0=empty, 1=tree, 2=burning)
        p_ignite: probability of spontaneous ignition
        fuel_map: 2D array of Anderson13 fuel codes (e.g. 'TL1', 'TU1', ...)
        fuel_spread_probs: dict mapping Anderson13 code to spread probability
        """
        self.grid_shape = grid_shape
        self.n_states = n_states
        self.p_ignite = p_ignite
        self.rng = np.random.default_rng(seed)
        self.grid = np.zeros(grid_shape, dtype=int)
        self.fuel_map = fuel_map
        self.fuel_spread_probs = fuel_spread_probs or {}

    def get_spread_prob(self, x, y):
        if self.fuel_map is not None and self.fuel_spread_probs:
            code = self.fuel_map[x, y]
            return self.fuel_spread_probs.get(code, 0.2)  # default prob
        return 0.2

    def initialize(self, tree_density=0.6):
        """Initialize grid with trees (state=1) and empty (state=0)"""
        self.grid = (self.rng.random(self.grid_shape) < tree_density).astype(int)

    def step(self):
        """One CA step: fire spreads, trees ignite, etc."""
        new_grid = self.grid.copy()
        burning = (self.grid == 2)
        # Burned cells become empty
        new_grid[burning] = 0
        # Spread fire to neighbors
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            neighbor = np.roll(np.roll(burning, dx, axis=0), dy, axis=1)
            ignite = (self.grid == 1) & neighbor
            if self.fuel_map is not None and self.fuel_spread_probs:
                # 셀별 확률적 번짐
                prob_map = np.zeros(self.grid_shape)
                for i in range(self.grid_shape[0]):
                    for j in range(self.grid_shape[1]):
                        prob_map[i, j] = self.get_spread_prob(i, j)
                rand_map = self.rng.random(self.grid_shape)
                ignite = ignite & (rand_map < prob_map)
            new_grid[ignite] = 2
        # Spontaneous ignition
        spontaneous = (self.grid == 1) & (self.rng.random(self.grid_shape) < self.p_ignite)
        new_grid[spontaneous] = 2
        self.grid = new_grid

    def ignite(self, x, y):
        """Manually ignite a cell (set to burning)"""
        self.grid[x, y] = 2

    def plot(self):
        plt.imshow(self.grid, cmap='hot', interpolation='nearest')
        plt.title('CA Model')
        plt.axis('off')
        plt.show()

if __name__ == "__main__":
    ca = CAModel((100, 100), n_states=3, p_ignite=0.0005, seed=42)
    ca.initialize(tree_density=0.7)
    ca.ignite(50, 50)
    for _ in range(100):
        ca.step()
        if _ % 10 == 0:
            ca.plot()
