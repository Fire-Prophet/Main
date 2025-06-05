#!/usr/bin/env python3
"""
통합 시스템 테스트 및 데모 스크립트
- 전체 시스템의 기능을 테스트
- 실제 사용 예제 제공
- 성능 벤치마크 실행
"""

import os
import sys
import time
import numpy as np
import json
from datetime import datetime
import argparse

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from integrated_validation_system import IntegratedValidationSystem
    from model_validation import ModelValidator, create_synthetic_actual_data
    from realistic_fire_model import RealisticFireModel, DetailedWeatherConditions, HumanActivity
    from advanced_ca_model import AdvancedCAFireModel
    from ca_analyzer import CAAnalyzer
except ImportError as e:
    print(f"❌ 모듈 임포트 오류: {e}")
    print("필요한 모든 파일이 같은 디렉토리에 있는지 확인하세요.")
    sys.exit(1)

class SystemTester:
    """시스템 통합 테스트 클래스"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        
    def run_all_tests(self, output_dir="test_results"):
        """모든 테스트 실행"""
        print("🚀 통합 시스템 테스트 시작")
        print("=" * 60)
        
        self.start_time = time.time()
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. 기본 모듈 테스트
        print("\n1️⃣ 기본 모듈 테스트")
        self.test_basic_modules()
        
        # 2. 검증 시스템 테스트
        print("\n2️⃣ 모델 검증 시스템 테스트")
        self.test_validation_system()
        
        # 3. 현실성 모듈 테스트
        print("\n3️⃣ 현실성 향상 모듈 테스트")
        self.test_realistic_model()
        
        # 4. 통합 시스템 테스트
        print("\n4️⃣ 통합 시스템 테스트")
        self.test_integrated_system(output_dir)
        
        # 5. 성능 벤치마크
        print("\n5️⃣ 성능 벤치마크")
        self.run_performance_benchmark()
        
        # 결과 요약
        self.print_test_summary()
        
        return self.test_results
    
    def test_basic_modules(self):
        """기본 모듈들 테스트"""
        tests = [
            ("CA 모델 초기화", self._test_ca_model),
            ("연료 맵 생성", self._test_fuel_map),
            ("기본 시뮬레이션", self._test_basic_simulation)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"  - {test_name}...", end=" ")
                result = test_func()
                self.test_results[test_name] = {"status": "✅ 성공", "result": result}
                print("✅")
            except Exception as e:
                self.test_results[test_name] = {"status": "❌ 실패", "error": str(e)}
                print(f"❌ ({e})")
    
    def test_validation_system(self):
        """검증 시스템 테스트"""
        tests = [
            ("검증기 초기화", self._test_validator_init),
            ("패턴 검증", self._test_pattern_validation),
            ("시간적 검증", self._test_temporal_validation),
            ("혼동 행렬 계산", self._test_confusion_matrix)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"  - {test_name}...", end=" ")
                result = test_func()
                self.test_results[test_name] = {"status": "✅ 성공", "result": result}
                print("✅")
            except Exception as e:
                self.test_results[test_name] = {"status": "❌ 실패", "error": str(e)}
                print(f"❌ ({e})")
    
    def test_realistic_model(self):
        """현실성 모듈 테스트"""
        tests = [
            ("현실적 모델 초기화", self._test_realistic_init),
            ("기상 조건 설정", self._test_weather_setup),
            ("비화 시뮬레이션", self._test_spotting),
            ("화재 행동 계산", self._test_fire_behavior)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"  - {test_name}...", end=" ")
                result = test_func()
                self.test_results[test_name] = {"status": "✅ 성공", "result": result}
                print("✅")
            except Exception as e:
                self.test_results[test_name] = {"status": "❌ 실패", "error": str(e)}
                print(f"❌ ({e})")
    
    def test_integrated_system(self, output_dir):
        """통합 시스템 테스트"""
        tests = [
            ("통합 시스템 초기화", lambda: self._test_integrated_init(output_dir)),
            ("모델 설정", self._test_model_setup),
            ("시뮬레이션 실행", self._test_simulation_run),
            ("보고서 생성", lambda: self._test_report_generation(output_dir))
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"  - {test_name}...", end=" ")
                result = test_func()
                self.test_results[test_name] = {"status": "✅ 성공", "result": result}
                print("✅")
            except Exception as e:
                self.test_results[test_name] = {"status": "❌ 실패", "error": str(e)}
                print(f"❌ ({e})")
    
    def run_performance_benchmark(self):
        """성능 벤치마크 실행"""
        print("  성능 측정 중...")
        
        grid_sizes = [(50, 50), (100, 100), (150, 150)]
        benchmark_results = {}
        
        for size in grid_sizes:
            try:
                start_time = time.time()
                
                # 테스트 시뮬레이션 실행
                ca_model = AdvancedCAFireModel(size)
                fuel_map = np.random.choice(['TL1', 'TL2', 'GS1'], size=size)
                ca_model.fuel_map = fuel_map
                
                # 간단한 시뮬레이션
                grid = np.zeros(size, dtype=int)
                center = (size[0]//2, size[1]//2)
                grid[center[0], center[1]] = 1
                
                for _ in range(10):  # 10단계만 실행
                    grid = ca_model._apply_fire_rules(grid)
                
                elapsed_time = time.time() - start_time
                benchmark_results[f"{size[0]}x{size[1]}"] = {
                    "time": elapsed_time,
                    "cells_per_second": (size[0] * size[1] * 10) / elapsed_time
                }
                
                print(f"    {size[0]}x{size[1]}: {elapsed_time:.3f}초")
                
            except Exception as e:
                benchmark_results[f"{size[0]}x{size[1]}"] = {"error": str(e)}
        
        self.test_results["성능 벤치마크"] = {"status": "✅ 완료", "result": benchmark_results}
    
    def _test_ca_model(self):
        """CA 모델 테스트"""
        model = AdvancedCAFireModel((50, 50))
        assert model.height == 50
        assert model.width == 50
        return {"grid_size": model.grid.shape}
    
    def _test_fuel_map(self):
        """연료 맵 테스트"""
        fuel_map = np.random.choice(['TL1', 'TL2', 'GS1'], size=(30, 30))
        unique_fuels = np.unique(fuel_map)
        return {"unique_fuels": len(unique_fuels), "map_size": fuel_map.shape}
    
    def _test_basic_simulation(self):
        """기본 시뮬레이션 테스트"""
        model = AdvancedCAFireModel((30, 30))
        model.fuel_map = np.random.choice(['TL1', 'GS1'], size=(30, 30))
        
        grid = np.zeros((30, 30), dtype=int)
        grid[15, 15] = 1  # 중앙에 화재
        
        new_grid = model._apply_fire_rules(grid)
        burned_cells = np.sum(new_grid > 0)
        
        return {"initial_fire": 1, "after_step": int(burned_cells)}
    
    def _test_validator_init(self):
        """검증기 초기화 테스트"""
        test_results = {
            'final_grid': np.random.randint(0, 3, size=(20, 20)),
            'step_history': [np.random.randint(0, 3, size=(20, 20)) for _ in range(5)],
            'fuel_map': np.random.choice(['TL1', 'GS1'], size=(20, 20))
        }
        
        validator = ModelValidator(test_results)
        return {"validator_created": True}
    
    def _test_pattern_validation(self):
        """패턴 검증 테스트"""
        test_grid = np.zeros((20, 20), dtype=int)
        test_grid[8:12, 8:12] = 2  # 작은 연소 영역
        
        test_results = {
            'final_grid': test_grid,
            'fuel_map': np.random.choice(['TL1'], size=(20, 20))
        }
        
        validator = ModelValidator(test_results)
        metrics = validator.validate_spread_pattern()
        
        return {
            "compactness": metrics.get('compactness', 0),
            "total_burned": metrics.get('total_burned_area', 0)
        }
    
    def _test_temporal_validation(self):
        """시간적 검증 테스트"""
        step_history = []
        for i in range(5):
            grid = np.zeros((20, 20), dtype=int)
            # 점진적으로 확산
            grid[9:11+i, 9:11+i] = 2
            step_history.append(grid)
        
        test_results = {
            'step_history': step_history,
            'fuel_map': np.random.choice(['TL1'], size=(20, 20))
        }
        
        validator = ModelValidator(test_results)
        metrics = validator.validate_temporal_progression()
        
        return {
            "growth_consistency": metrics.get('growth_consistency', 0),
            "mean_rate": metrics['burn_rate_progression'].get('mean_rate', 0)
        }
    
    def _test_confusion_matrix(self):
        """혼동 행렬 테스트"""
        predicted = np.random.randint(0, 2, size=(20, 20))
        actual = np.random.randint(0, 2, size=(20, 20))
        
        test_results = {'final_grid': predicted}
        validator = ModelValidator(test_results)
        
        metrics = validator.calculate_confusion_matrix(actual)
        
        return {
            "accuracy": metrics.get('accuracy', 0),
            "f1_score": metrics.get('f1_score', 0)
        }
    
    def _test_realistic_init(self):
        """현실적 모델 초기화 테스트"""
        model = RealisticFireModel((30, 30), cell_size=30.0)
        return {"grid_size": (model.height, model.width), "cell_size": model.cell_size}
    
    def _test_weather_setup(self):
        """기상 조건 설정 테스트"""
        weather = DetailedWeatherConditions(
            temperature=30.0,
            relative_humidity=40.0,
            wind_speed=10.0,
            wind_direction=180.0,
            atmospheric_pressure=1013.0,
            solar_radiation=600.0,
            precipitation=0.0,
            drought_index=0.6,
            fire_weather_index=70.0,
            stability_class='C'
        )
        
        return {
            "temperature": weather.temperature,
            "wind_speed": weather.wind_speed,
            "fire_weather_index": weather.fire_weather_index
        }
    
    def _test_spotting(self):
        """비화 테스트"""
        model = RealisticFireModel((30, 30))
        model.weather_conditions = DetailedWeatherConditions(
            temperature=35.0, relative_humidity=20.0, wind_speed=20.0,
            wind_direction=270.0, atmospheric_pressure=1013.0,
            solar_radiation=800.0, precipitation=0.0,
            drought_index=0.8, fire_weather_index=90.0, stability_class='B'
        )
        
        # 강한 화재 조건
        model.ember_source_map = np.zeros((30, 30))
        model.ember_source_map[15, 15] = 1.0  # 강한 불씨 생성
        
        grid = np.zeros((30, 30), dtype=int)
        grid[15, 15] = 1
        
        new_ignitions = model.simulate_spotting(grid, max_spot_distance=500)
        
        return {
            "spotting_events": len(new_ignitions),
            "wind_speed": model.weather_conditions.wind_speed
        }
    
    def _test_fire_behavior(self):
        """화재 행동 계산 테스트"""
        model = RealisticFireModel((20, 20))
        model.fuel_map = np.random.choice(['TL1', 'TL2'], size=(20, 20))
        
        grid = np.zeros((20, 20), dtype=int)
        grid[10, 10] = 1
        
        behavior_data = model.calculate_fire_behavior(grid)
        
        return {
            "max_intensity": float(np.max(behavior_data['fire_intensity'])),
            "max_flame_length": float(np.max(behavior_data['flame_length']))
        }
    
    def _test_integrated_init(self, output_dir):
        """통합 시스템 초기화 테스트"""
        self.integrated_system = IntegratedValidationSystem()
        self.integrated_system.config['output']['output_directory'] = output_dir
        return {"config_loaded": True}
    
    def _test_model_setup(self):
        """모델 설정 테스트"""
        fuel_map = np.random.choice(['TL1', 'TL2', 'GS1'], size=(40, 40))
        elevation_map = np.random.randint(100, 500, size=(40, 40))
        
        weather_data = {
            'temperature': 30.0,
            'relative_humidity': 35.0,
            'wind_speed': 15.0,
            'wind_direction': 180.0,
            'atmospheric_pressure': 1013.0,
            'solar_radiation': 700.0,
            'precipitation': 0.0,
            'drought_index': 0.7,
            'fire_weather_index': 80.0,
            'stability_class': 'C'
        }
        
        self.integrated_system.setup_models(fuel_map, elevation_map, weather_data)
        return {"models_setup": True}
    
    def _test_simulation_run(self):
        """시뮬레이션 실행 테스트"""
        ignition_points = [(20, 20)]
        
        # 짧은 시뮬레이션으로 테스트
        self.integrated_system.config['simulation']['max_steps'] = 10
        
        results = self.integrated_system.run_integrated_simulation(ignition_points)
        
        return {
            "total_steps": results.get('total_steps', 0),
            "final_burned": int(np.sum(results['final_grid'] == 2))
        }
    
    def _test_report_generation(self, output_dir):
        """보고서 생성 테스트"""
        # 간단한 검증 실행
        validation_results = self.integrated_system.run_comprehensive_validation()
        
        # 보고서 생성
        report_path = self.integrated_system.generate_comprehensive_report(output_dir)
        
        return {
            "report_generated": os.path.exists(report_path),
            "report_path": report_path
        }
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if result['status'].startswith('✅'))
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests} ✅")
        print(f"실패: {failed_tests} ❌")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.start_time:
            total_time = time.time() - self.start_time
            print(f"총 소요 시간: {total_time:.2f}초")
        
        # 실패한 테스트 상세 정보
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for test_name, result in self.test_results.items():
                if result['status'].startswith('❌'):
                    print(f"  - {test_name}: {result.get('error', '알 수 없는 오류')}")
        
        print("\n" + "=" * 60)

def create_demo_scenario():
    """데모 시나리오 실행"""
    print("🎬 데모 시나리오: 산불 확산 시뮬레이션")
    print("=" * 60)
    
    # 시나리오 설정
    print("\n📋 시나리오 설정:")
    print("- 위치: 가상의 산림 지역 (100x100 격자)")
    print("- 연료: 혼합림 (침엽수림, 활엽수림, 관목)")
    print("- 기상: 건조하고 바람이 강한 조건")
    print("- 착화: 캠핑장 근처에서 발생")
    
    # 시스템 초기화
    system = IntegratedValidationSystem()
    
    # 현실적인 데이터 생성
    grid_size = (100, 100)
    
    # 연료 맵 (현실적인 분포)
    fuel_map = np.full(grid_size, 'TL1', dtype='<U3')
    
    # 침엽수림 지역 (화재 위험 높음)
    fuel_map[20:60, 20:60] = 'TL2'
    fuel_map[30:50, 30:50] = 'TL3'
    
    # 관목 지역
    fuel_map[60:80, 40:80] = 'TU2'
    
    # 초지 지역
    fuel_map[10:30, 70:90] = 'GS2'
    fuel_map[70:90, 10:30] = 'GR1'
    
    # 지형 (고도 변화)
    x, y = np.meshgrid(np.linspace(0, 10, 100), np.linspace(0, 10, 100))
    elevation_map = (200 + 300 * np.sin(x) * np.cos(y) + 
                    100 * np.random.random(grid_size)).astype(int)
    
    # 위험한 기상 조건
    weather_data = {
        'temperature': 38.0,        # 높은 온도
        'relative_humidity': 18.0,  # 낮은 습도
        'wind_speed': 25.0,         # 강한 바람
        'wind_direction': 225.0,    # 남서풍
        'atmospheric_pressure': 1008.0,
        'solar_radiation': 900.0,
        'precipitation': 0.0,       # 무강수
        'drought_index': 0.9,       # 극심한 가뭄
        'fire_weather_index': 95.0, # 극도로 위험
        'stability_class': 'A'      # 불안정한 대기
    }
    
    # 인간 활동 (캠핑장, 도로)
    human_data = {
        'population_density': 0.2,
        'road_density': 0.4,
        'recreation_areas': [(15, 15), (25, 20)],  # 캠핑장
        'industrial_sites': [],
        'power_lines': [(10, 10, 90, 90)],  # 송전선
        'ignition_risk_map': np.random.random(grid_size) * 0.5
    }
    
    print("\n🔧 모델 설정 중...")
    system.setup_models(fuel_map, elevation_map, weather_data, human_data)
    
    print("\n🔥 시뮬레이션 실행 중...")
    # 캠핑장 근처에서 착화
    ignition_points = [(18, 18), (22, 22)]
    
    # 더 긴 시뮬레이션
    system.config['simulation']['max_steps'] = 50
    system.config['simulation']['validation_interval'] = 10
    
    results = system.run_integrated_simulation(ignition_points)
    
    print("\n📊 검증 분석 중...")
    validation_results = system.run_comprehensive_validation()
    
    print("\n📄 보고서 생성 중...")
    report_path = system.generate_comprehensive_report("demo_scenario_results")
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📈 시뮬레이션 결과")
    print("=" * 60)
    
    final_grid = results['final_grid']
    total_burned = np.sum(final_grid == 2)
    total_cells = final_grid.size
    
    print(f"총 연소 면적: {total_burned:,} 셀 ({total_burned * 30 * 30 / 10000:.1f} ha)")
    print(f"연소 비율: {(total_burned/total_cells)*100:.2f}%")
    print(f"시뮬레이션 단계: {results['total_steps']}")
    
    # 현실성 지표
    if hasattr(system.realistic_model, 'spotting_events'):
        print(f"비화 이벤트: {len(system.realistic_model.spotting_events)}회")
    
    if 'confusion_matrix' in validation_results:
        cm = validation_results['confusion_matrix']
        print(f"모델 정확도: {cm.get('accuracy', 0):.3f}")
    
    print(f"\n📁 상세 결과: {report_path}")
    print("\n🎉 데모 시나리오 완료!")
    
    return system, results

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='통합 화재 시뮬레이션 테스트')
    parser.add_argument('--mode', choices=['test', 'demo', 'both'], default='both',
                       help='실행 모드 선택')
    parser.add_argument('--output', default='test_results',
                       help='결과 저장 디렉토리')
    
    args = parser.parse_args()
    
    print("🔥 한국 산림 화재 확산 시뮬레이션 시스템")
    print("=" * 60)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"실행 모드: {args.mode}")
    print(f"결과 저장: {args.output}")
    
    if args.mode in ['test', 'both']:
        print("\n🧪 시스템 테스트 실행")
        tester = SystemTester()
        test_results = tester.run_all_tests(args.output)
        
        # 테스트 결과 저장
        with open(os.path.join(args.output, 'test_results.json'), 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)
    
    if args.mode in ['demo', 'both']:
        print("\n🎬 데모 시나리오 실행")
        demo_system, demo_results = create_demo_scenario()
    
    print(f"\n✅ 모든 작업 완료! 결과는 '{args.output}' 디렉토리에서 확인하세요.")

if __name__ == "__main__":
    main()
