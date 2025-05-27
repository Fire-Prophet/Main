"""
화재 시뮬레이션 성능 최적화 모듈
Numba JIT 컴파일, 병렬 처리, 메모리 최적화 기능
"""

import numpy as np
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial
import time
from typing import Tuple, List, Optional
import warnings

# Numba JIT 컴파일 (선택적 설치)
try:
    from numba import jit, njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Numba가 없을 때 더미 데코레이터
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    prange = range

class PerformanceOptimizer:
    """성능 최적화 도구"""
    
    def __init__(self, use_numba: bool = True, use_parallel: bool = True):
        self.use_numba = use_numba and NUMBA_AVAILABLE
        self.use_parallel = use_parallel
        self.num_cores = mp.cpu_count()
        
        if not NUMBA_AVAILABLE and use_numba:
            warnings.warn("Numba not available. Install with: pip install numba")
    
    @staticmethod
    @njit(cache=True)
    def fast_neighbor_check(grid: np.ndarray, x: int, y: int, 
                           neighborhood: str = 'moore') -> np.ndarray:
        """빠른 이웃 셀 확인 (Numba 최적화)"""
        height, width = grid.shape
        neighbors = np.zeros((8, 2), dtype=np.int32)
        count = 0
        
        if neighborhood == 'moore':
            # Moore 이웃 (8방향)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < height and 0 <= ny < width:
                        neighbors[count, 0] = nx
                        neighbors[count, 1] = ny
                        count += 1
        else:
            # Von Neumann 이웃 (4방향)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < height and 0 <= ny < width:
                    neighbors[count, 0] = nx
                    neighbors[count, 1] = ny
                    count += 1
        
        return neighbors[:count]
    
    @staticmethod
    @njit(cache=True, parallel=True)
    def fast_fire_spread(grid: np.ndarray, spread_probs: np.ndarray,
                        burn_timer: np.ndarray, rng_state: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """빠른 화재 확산 계산 (Numba 병렬 처리)"""
        height, width = grid.shape
        new_grid = grid.copy()
        new_burn_timer = burn_timer.copy()
        
        # 연소 중인 셀들 찾기
        burning_cells = np.where(grid == 2)
        
        for idx in prange(len(burning_cells[0])):
            i, j = burning_cells[0][idx], burning_cells[1][idx]
            
            # 8방향 이웃 확인
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    if di == 0 and dj == 0:
                        continue
                    
                    ni, nj = i + di, j + dj
                    if 0 <= ni < height and 0 <= nj < width:
                        if grid[ni, nj] == 1:  # 나무
                            # 확산 확률 체크
                            rand_val = np.random.random()
                            if rand_val < spread_probs[ni, nj]:
                                new_grid[ni, nj] = 2  # 점화
                                new_burn_timer[ni, nj] = 0
            
            # 연소 시간 증가
            new_burn_timer[i, j] += 1
            
            # 연소 완료 체크
            if new_burn_timer[i, j] >= 3:  # 기본 연소 시간
                new_grid[i, j] = 3  # 연소 완료
        
        return new_grid, new_burn_timer
    
    @staticmethod
    @njit(cache=True)
    def fast_heat_diffusion(heat_map: np.ndarray, diffusion_rate: float = 0.1) -> np.ndarray:
        """빠른 열 확산 계산"""
        height, width = heat_map.shape
        new_heat = heat_map.copy()
        
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                # 5점 스텐실로 열 확산
                avg_heat = (
                    heat_map[i-1, j] + heat_map[i+1, j] + 
                    heat_map[i, j-1] + heat_map[i, j+1] + 
                    heat_map[i, j]
                ) / 5.0
                
                new_heat[i, j] = heat_map[i, j] + diffusion_rate * (avg_heat - heat_map[i, j])
        
        # 열 감소 (냉각)
        new_heat *= 0.95
        
        return new_heat
    
    @staticmethod
    @njit(cache=True)
    def calculate_fire_perimeter_fast(burning_mask: np.ndarray) -> int:
        """빠른 화재 경계선 계산"""
        height, width = burning_mask.shape
        perimeter = 0
        
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                if burning_mask[i, j]:
                    # 이웃 중 하나라도 비연소 상태면 경계
                    neighbors = [
                        burning_mask[i-1, j], burning_mask[i+1, j],
                        burning_mask[i, j-1], burning_mask[i, j+1]
                    ]
                    if not all(neighbors):
                        perimeter += 1
        
        return perimeter

class OptimizedCAModel:
    """성능 최적화된 CA 모델"""
    
    def __init__(self, grid_shape: Tuple[int, int], 
                 use_optimization: bool = True, 
                 chunk_size: Optional[int] = None):
        """
        grid_shape: 격자 크기
        use_optimization: 최적화 사용 여부
        chunk_size: 병렬 처리 청크 크기
        """
        self.grid_shape = grid_shape
        self.optimizer = PerformanceOptimizer(use_numba=use_optimization)
        self.chunk_size = chunk_size or max(1, grid_shape[0] // self.optimizer.num_cores)
        
        # 상태 배열들
        self.grid = np.zeros(grid_shape, dtype=np.int32)
        self.spread_probs = np.full(grid_shape, 0.15, dtype=np.float32)
        self.burn_timer = np.zeros(grid_shape, dtype=np.int32)
        self.heat_map = np.zeros(grid_shape, dtype=np.float32)
        
        # 성능 모니터링
        self.timing_stats = {
            'spread_calculation': [],
            'heat_diffusion': [],
            'statistics': [],
            'total_step': []
        }
    
    def set_fuel_properties(self, fuel_map: np.ndarray, fuel_properties: dict):
        """연료 특성 설정 (벡터화)"""
        # 연료별 확산 확률 매핑 (벡터화)
        for fuel_type, props in fuel_properties.items():
            mask = (fuel_map == fuel_type)
            self.spread_probs[mask] = props.get('spread_prob', 0.15)
    
    def step_optimized(self) -> dict:
        """최적화된 시뮬레이션 스텝"""
        step_start = time.time()
        
        # 1. 화재 확산 계산 (Numba 최적화)
        spread_start = time.time()
        if self.optimizer.use_numba:
            self.grid, self.burn_timer = PerformanceOptimizer.fast_fire_spread(
                self.grid, self.spread_probs, self.burn_timer, 
                np.random.randint(0, 2**31, size=self.grid_shape, dtype=np.int32)
            )
        else:
            self._spread_fallback()
        
        spread_time = time.time() - spread_start
        self.timing_stats['spread_calculation'].append(spread_time)
        
        # 2. 열 확산 계산
        heat_start = time.time()
        if self.optimizer.use_numba:
            self.heat_map = PerformanceOptimizer.fast_heat_diffusion(self.heat_map)
        else:
            self._heat_diffusion_fallback()
        
        heat_time = time.time() - heat_start
        self.timing_stats['heat_diffusion'].append(heat_time)
        
        # 3. 통계 계산
        stats_start = time.time()
        stats = self._calculate_stats_optimized()
        stats_time = time.time() - stats_start
        self.timing_stats['statistics'].append(stats_time)
        
        total_time = time.time() - step_start
        self.timing_stats['total_step'].append(total_time)
        
        return stats
    
    def _spread_fallback(self):
        """Numba 없을 때 대체 구현"""
        new_grid = self.grid.copy()
        burning_cells = np.where(self.grid == 2)
        
        for i, j in zip(burning_cells[0], burning_cells[1]):
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if (0 <= ni < self.grid_shape[0] and 
                        0 <= nj < self.grid_shape[1] and
                        self.grid[ni, nj] == 1):
                        
                        if np.random.random() < self.spread_probs[ni, nj]:
                            new_grid[ni, nj] = 2
            
            self.burn_timer[i, j] += 1
            if self.burn_timer[i, j] >= 3:
                new_grid[i, j] = 3
        
        self.grid = new_grid
    
    def _heat_diffusion_fallback(self):
        """열 확산 대체 구현"""
        from scipy import ndimage
        self.heat_map = ndimage.gaussian_filter(self.heat_map, sigma=0.5)
        self.heat_map *= 0.95
    
    def _calculate_stats_optimized(self) -> dict:
        """최적화된 통계 계산"""
        # 벡터화된 계산
        unique, counts = np.unique(self.grid, return_counts=True)
        state_counts = dict(zip(unique, counts))
        
        # 화재 경계선 계산
        burning_mask = (self.grid == 2)
        if self.optimizer.use_numba:
            perimeter = PerformanceOptimizer.calculate_fire_perimeter_fast(burning_mask)
        else:
            from scipy import ndimage
            eroded = ndimage.binary_erosion(burning_mask)
            perimeter = np.sum(burning_mask.astype(int) - eroded.astype(int))
        
        return {
            'empty_cells': state_counts.get(0, 0),
            'tree_cells': state_counts.get(1, 0),
            'burning_cells': state_counts.get(2, 0),
            'burned_cells': state_counts.get(3, 0),
            'fire_perimeter': int(perimeter),
            'total_heat': float(np.sum(self.heat_map)),
            'burn_ratio': state_counts.get(3, 0) / self.grid.size
        }
    
    def run_parallel_simulation(self, steps: int, num_processes: int = None) -> List[dict]:
        """병렬 시뮬레이션 실행"""
        if num_processes is None:
            num_processes = min(4, self.optimizer.num_cores)
        
        # 시뮬레이션을 청크로 분할
        chunk_steps = max(1, steps // num_processes)
        chunks = []
        
        for i in range(0, steps, chunk_steps):
            end_step = min(i + chunk_steps, steps)
            chunks.append((i, end_step))
        
        # 병렬 실행
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            futures = []
            for start_step, end_step in chunks:
                future = executor.submit(self._run_chunk, start_step, end_step)
                futures.append(future)
            
            results = []
            for future in futures:
                chunk_results = future.result()
                results.extend(chunk_results)
        
        return results
    
    def _run_chunk(self, start_step: int, end_step: int) -> List[dict]:
        """시뮬레이션 청크 실행"""
        results = []
        for step in range(start_step, end_step):
            stats = self.step_optimized()
            stats['step'] = step
            results.append(stats)
        return results
    
    def get_performance_report(self) -> dict:
        """성능 리포트 생성"""
        report = {}
        
        for operation, times in self.timing_stats.items():
            if times:
                report[operation] = {
                    'mean_time': np.mean(times),
                    'total_time': np.sum(times),
                    'min_time': np.min(times),
                    'max_time': np.max(times),
                    'std_time': np.std(times),
                    'count': len(times)
                }
        
        # 전체 성능 지표
        if self.timing_stats['total_step']:
            total_steps = len(self.timing_stats['total_step'])
            total_time = np.sum(self.timing_stats['total_step'])
            
            report['overall'] = {
                'total_steps': total_steps,
                'total_time': total_time,
                'steps_per_second': total_steps / total_time if total_time > 0 else 0,
                'optimization_enabled': self.optimizer.use_numba,
                'numba_available': NUMBA_AVAILABLE,
                'cpu_cores': self.optimizer.num_cores
            }
        
        return report

class MemoryOptimizer:
    """메모리 사용량 최적화"""
    
    @staticmethod
    def optimize_dtypes(arrays: dict) -> dict:
        """데이터 타입 최적화"""
        optimized = {}
        
        for name, array in arrays.items():
            if 'grid' in name or 'state' in name:
                # 상태 배열은 int8로 충분
                optimized[name] = array.astype(np.int8)
            elif 'prob' in name or 'heat' in name:
                # 확률/열 배열은 float32로 충분
                optimized[name] = array.astype(np.float32)
            elif 'timer' in name or 'count' in name:
                # 타이머/카운터는 int16으로 충분
                optimized[name] = array.astype(np.int16)
            else:
                optimized[name] = array
        
        return optimized
    
    @staticmethod
    def create_memory_efficient_grid(shape: Tuple[int, int]) -> dict:
        """메모리 효율적인 격자 생성"""
        return {
            'grid': np.zeros(shape, dtype=np.int8),
            'spread_probs': np.zeros(shape, dtype=np.float32),
            'burn_timer': np.zeros(shape, dtype=np.int16),
            'heat_map': np.zeros(shape, dtype=np.float32)
        }

# 사용 예시 및 성능 테스트
def performance_benchmark():
    """성능 벤치마크"""
    print("화재 시뮬레이션 성능 벤치마크")
    print("=" * 50)
    
    # 테스트 설정
    grid_sizes = [(50, 50), (100, 100), (200, 200)]
    test_steps = 10
    
    for grid_size in grid_sizes:
        print(f"\n격자 크기: {grid_size}")
        
        # 최적화된 모델
        model_opt = OptimizedCAModel(grid_size, use_optimization=True)
        model_opt.grid[grid_size[0]//2, grid_size[1]//2] = 2  # 중앙 점화
        model_opt.grid[model_opt.grid == 0] = np.random.choice([0, 1], 
                                                               size=np.sum(model_opt.grid == 0), 
                                                               p=[0.3, 0.7])
        
        # 성능 테스트
        start_time = time.time()
        for _ in range(test_steps):
            model_opt.step_optimized()
        opt_time = time.time() - start_time
        
        # 성능 리포트
        report = model_opt.get_performance_report()
        
        print(f"  최적화 모델: {opt_time:.3f}초 ({test_steps} 스텝)")
        if 'overall' in report:
            print(f"  스텝/초: {report['overall']['steps_per_second']:.1f}")
            print(f"  Numba 사용: {report['overall']['optimization_enabled']}")
        
        # 메모리 사용량
        memory_info = MemoryOptimizer.create_memory_efficient_grid(grid_size)
        total_memory = sum(arr.nbytes for arr in memory_info.values()) / 1024 / 1024
        print(f"  메모리 사용량: {total_memory:.2f} MB")

if __name__ == '__main__':
    performance_benchmark()
