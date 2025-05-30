#!/usr/bin/env python3
"""
화재 시뮬레이션 시스템 종합 테스트 스위트
"""

import unittest
import numpy as np
import tempfile
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from ca_base import CellularAutomaton
from model_validation import ModelValidator
from realistic_fire_model import RealisticFireModel
from integrated_validation_system import IntegratedValidationSystem


class TestCellularAutomaton(unittest.TestCase):
    """CA 모델 기본 테스트"""
    
    def setUp(self):
        """테스트 환경 설정"""
        self.ca = CellularAutomaton(grid_size=(10, 10))
        
    def test_initialization(self):
        """초기화 테스트"""
        self.assertEqual(self.ca.grid.shape, (10, 10))
        self.assertEqual(self.ca.step_count, 0)
        
    def test_ignition(self):
        """점화 테스트"""
        ignition_points = [(5, 5)]
        self.ca.ignite(ignition_points)
        self.assertTrue(self.ca.grid[5, 5] > 0)
        
    def test_step_execution(self):
        """시뮬레이션 스텝 실행 테스트"""
        self.ca.ignite([(5, 5)])
        initial_fire_count = np.sum(self.ca.grid > 0)
        self.ca.step()
        self.assertEqual(self.ca.step_count, 1)
        
    def test_boundary_conditions(self):
        """경계 조건 테스트"""
        # 경계에서 점화
        self.ca.ignite([(0, 0)])
        self.ca.step()
        # 격자 밖으로 나가지 않는지 확인
        self.assertTrue(np.all(self.ca.grid >= 0))


class TestModelValidator(unittest.TestCase):
    """모델 검증 시스템 테스트"""
    
    def setUp(self):
        """테스트 환경 설정"""
        # 가상의 시뮬레이션 결과 생성
        self.mock_results = {
            'grids': [np.random.randint(0, 4, (20, 20)) for _ in range(10)],
            'fuel_map': np.random.randint(1, 14, (20, 20)),
            'metadata': {
                'steps': 10,
                'grid_size': (20, 20),
                'cell_size': 30.0
            }
        }
        self.validator = ModelValidator(self.mock_results)
        
    def test_spread_pattern_validation(self):
        """확산 패턴 검증 테스트"""
        metrics = self.validator.validate_spread_pattern()
        self.assertIn('compactness', metrics)
        self.assertIn('circularity', metrics)
        self.assertIsInstance(metrics['compactness'], (int, float))
        
    def test_temporal_progression_validation(self):
        """시간적 진행 검증 테스트"""
        metrics = self.validator.validate_temporal_progression()
        self.assertIn('growth_consistency', metrics)
        self.assertIn('burn_rate_stability', metrics)
        
    def test_confusion_matrix_calculation(self):
        """혼동행렬 계산 테스트"""
        actual = np.random.randint(0, 2, (20, 20))
        predicted = np.random.randint(0, 2, (20, 20))
        
        metrics = self.validator.calculate_confusion_matrix(actual, predicted)
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1_score', metrics)


class TestRealisticFireModel(unittest.TestCase):
    """현실성 화재 모델 테스트"""
    
    def setUp(self):
        """테스트 환경 설정"""
        self.fire_model = RealisticFireModel(grid_size=(15, 15), cell_size=30.0)
        self.fire_model.fuel_map = np.random.randint(1, 14, (15, 15))
        
    def test_fire_intensity_calculation(self):
        """화재 강도 계산 테스트"""
        grid = np.zeros((15, 15))
        grid[7, 7] = 2  # 연소 중인 셀
        
        intensity = self.fire_model.calculate_fire_intensity(grid)
        self.assertIsInstance(intensity, np.ndarray)
        self.assertEqual(intensity.shape, (15, 15))
        
    def test_spotting_simulation(self):
        """비화 시뮬레이션 테스트"""
        grid = np.zeros((15, 15))
        grid[5:8, 5:8] = 2  # 화재 영역
        
        new_ignitions = self.fire_model.simulate_spotting(grid, max_spot_distance=500.0)
        self.assertIsInstance(new_ignitions, list)
        
    def test_weather_influence(self):
        """기상 영향 테스트"""
        # 기본 확산과 바람 영향 확산 비교
        grid_no_wind = self.fire_model.apply_weather_influence(
            np.ones((15, 15)) * 0.3,  # 기본 확산 확률
            wind_speed=0.0
        )
        
        grid_with_wind = self.fire_model.apply_weather_influence(
            np.ones((15, 15)) * 0.3,
            wind_speed=15.0,
            wind_direction=90.0
        )
        
        # 바람이 있을 때 확산 확률이 달라져야 함
        self.assertFalse(np.array_equal(grid_no_wind, grid_with_wind))


class TestIntegratedSystem(unittest.TestCase):
    """통합 시스템 테스트"""
    
    def setUp(self):
        """테스트 환경 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.system = IntegratedValidationSystem()
        
    def tearDown(self):
        """테스트 환경 정리"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_system_initialization(self):
        """시스템 초기화 테스트"""
        self.assertIsNotNone(self.system.ca_model)
        self.assertIsNotNone(self.system.realistic_model)
        self.assertIsNotNone(self.system.validator)
        
    def test_configuration_loading(self):
        """설정 파일 로딩 테스트"""
        config_path = os.path.join(self.temp_dir, "test_config.json")
        test_config = {
            "simulation": {
                "grid_size": [50, 50],
                "max_steps": 100
            },
            "validation": {
                "enable_pattern_validation": True
            }
        }
        
        import json
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)
            
        system = IntegratedValidationSystem(config_path)
        self.assertEqual(system.config['simulation']['grid_size'], [50, 50])


class TestPerformance(unittest.TestCase):
    """성능 테스트"""
    
    def test_large_grid_performance(self):
        """대형 격자 성능 테스트"""
        import time
        
        ca = CellularAutomaton(grid_size=(100, 100))
        ca.ignite([(50, 50)])
        
        start_time = time.time()
        for _ in range(10):
            ca.step()
        end_time = time.time()
        
        # 10 스텝이 5초 이내에 완료되어야 함
        self.assertLess(end_time - start_time, 5.0)
        
    def test_memory_usage(self):
        """메모리 사용량 테스트"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 큰 시뮬레이션 실행
        ca = CellularAutomaton(grid_size=(200, 200))
        ca.ignite([(100, 100)])
        for _ in range(20):
            ca.step()
            
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 메모리 증가가 500MB 이하여야 함
        self.assertLess(memory_increase, 500)


def create_test_suite():
    """테스트 스위트 생성"""
    suite = unittest.TestSuite()
    
    # 기본 기능 테스트
    suite.addTest(unittest.makeSuite(TestCellularAutomaton))
    suite.addTest(unittest.makeSuite(TestModelValidator))
    suite.addTest(unittest.makeSuite(TestRealisticFireModel))
    suite.addTest(unittest.makeSuite(TestIntegratedSystem))
    
    # 성능 테스트
    suite.addTest(unittest.makeSuite(TestPerformance))
    
    return suite


def run_tests(verbosity=2):
    """테스트 실행"""
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # 테스트 결과 요약
    print(f"\n{'='*50}")
    print(f"테스트 완료: {result.testsRun}개 실행")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}개")
    print(f"실패: {len(result.failures)}개")
    print(f"오류: {len(result.errors)}개")
    print(f"{'='*50}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # 커맨드라인에서 실행할 때
    import argparse
    
    parser = argparse.ArgumentParser(description='화재 시뮬레이션 테스트 스위트')
    parser.add_argument('--verbose', '-v', action='store_true', 
                      help='상세한 출력')
    parser.add_argument('--pattern', '-p', type=str, 
                      help='특정 테스트 패턴만 실행')
    
    args = parser.parse_args()
    
    if args.pattern:
        # 특정 패턴의 테스트만 실행
        suite = unittest.TestLoader().loadTestsFromName(args.pattern)
        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        runner.run(suite)
    else:
        # 전체 테스트 실행
        success = run_tests(verbosity=2 if args.verbose else 1)
        sys.exit(0 if success else 1)
