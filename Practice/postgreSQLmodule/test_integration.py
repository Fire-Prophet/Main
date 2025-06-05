#!/usr/bin/env python3
"""
🧪 PostgreSQL 화재 시뮬레이션 모듈 테스트
========================================

모든 모듈이 올바르게 작동하는지 확인하는 통합 테스트 스크립트
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(current_dir))
sys.path.append(str(parent_dir))

def test_module_imports():
    """모듈 임포트 테스트"""
    print("🔍 모듈 임포트 테스트...")
    
    try:
        from spatial_data_extractor import SpatialDataExtractor
        print("  ✅ SpatialDataExtractor 임포트 성공")
    except Exception as e:
        print(f"  ❌ SpatialDataExtractor 임포트 실패: {e}")
        return False
    
    try:
        from forest_data_processor import ForestDataProcessor
        print("  ✅ ForestDataProcessor 임포트 성공")
    except Exception as e:
        print(f"  ❌ ForestDataProcessor 임포트 실패: {e}")
        return False
    
    try:
        from soil_data_processor import SoilDataProcessor
        print("  ✅ SoilDataProcessor 임포트 성공")
    except Exception as e:
        print(f"  ❌ SoilDataProcessor 임포트 실패: {e}")
        return False
    
    try:
        from fire_simulation_connector import FireSimulationConnector
        print("  ✅ FireSimulationConnector 임포트 성공")
    except Exception as e:
        print(f"  ❌ FireSimulationConnector 임포트 실패: {e}")
        return False
    
    try:
        from fire_model_integrator import FireModelIntegrator
        print("  ✅ FireModelIntegrator 임포트 성공")
    except Exception as e:
        print(f"  ❌ FireModelIntegrator 임포트 실패: {e}")
        return False
    
    return True

def test_forest_processor():
    """산림 데이터 처리기 테스트"""
    print("\n🌲 ForestDataProcessor 테스트...")
    
    try:
        from forest_data_processor import ForestDataProcessor
        
        # 샘플 데이터 생성
        sample_data = pd.DataFrame({
            'id': [1, 2, 3, 4],
            'forest_type': ['소나무림', '활엽수림', '혼효림', '기타'],
            'density': [0.8, 0.6, 0.7, 0.3],
            'geom': [
                'POLYGON((127.0 37.0, 127.1 37.0, 127.1 37.1, 127.0 37.1, 127.0 37.0))',
                'POLYGON((127.1 37.0, 127.2 37.0, 127.2 37.1, 127.1 37.1, 127.1 37.0))',
                'POLYGON((127.0 37.1, 127.1 37.1, 127.1 37.2, 127.0 37.2, 127.0 37.1))',
                'POLYGON((127.1 37.1, 127.2 37.1, 127.2 37.2, 127.1 37.2, 127.1 37.1))'
            ]
        })
        
        processor = ForestDataProcessor()
        processed_data = processor.process_forest_data(sample_data)
        
        print(f"  ✅ 산림 데이터 처리 성공: {len(processed_data)}개 레코드")
        print(f"  📊 연료 모델 타입: {processed_data['fuel_model'].unique()}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 산림 데이터 처리 실패: {e}")
        return False

def test_soil_processor():
    """토양 데이터 처리기 테스트"""
    print("\n🏔️ SoilDataProcessor 테스트...")
    
    try:
        from soil_data_processor import SoilDataProcessor
        
        # 샘플 데이터 생성
        sample_data = pd.DataFrame({
            'id': [1, 2, 3],
            'soil_type': ['사질토', '점토', '양토'],
            'moisture_content': [25.0, 40.0, 30.0],
            'organic_matter': [3.5, 5.2, 4.1],
            'drainage': [3, 1, 2],
            'geom': [
                'POLYGON((127.0 37.0, 127.1 37.0, 127.1 37.1, 127.0 37.1, 127.0 37.0))',
                'POLYGON((127.1 37.0, 127.2 37.0, 127.2 37.1, 127.1 37.1, 127.1 37.0))',
                'POLYGON((127.0 37.1, 127.1 37.1, 127.1 37.2, 127.0 37.2, 127.0 37.1))'
            ]
        })
        
        processor = SoilDataProcessor()
        processed_data = processor.process_soil_data(sample_data)
        
        print(f"  ✅ 토양 데이터 처리 성공: {len(processed_data)}개 레코드")
        print(f"  📊 화재 위험 지수 범위: {processed_data['fire_risk_score'].min():.1f}-{processed_data['fire_risk_score'].max():.1f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 토양 데이터 처리 실패: {e}")
        return False

def test_simulation_connector():
    """시뮬레이션 연결기 테스트"""
    print("\n🔗 FireSimulationConnector 테스트...")
    
    try:
        from fire_simulation_connector import FireSimulationConnector
        from forest_data_processor import ForestDataProcessor
        from soil_data_processor import SoilDataProcessor
        
        # 샘플 데이터 준비
        forest_data = pd.DataFrame({
            'fuel_model': ['TL2', 'TL3', 'GR2'],
            'centroid_lng': [127.1, 127.2, 127.3],
            'centroid_lat': [37.1, 37.2, 37.3]
        })
        
        soil_data = pd.DataFrame({
            'moisture_content': [30, 40, 20],
            'fire_risk_index': [6, 4, 8],
            'centroid_lng': [127.15, 127.25, 127.35],
            'centroid_lat': [37.15, 37.25, 37.35]
        })
        
        elevation_data = pd.DataFrame({
            'longitude': [127.1, 127.2, 127.3],
            'latitude': [37.1, 37.2, 37.3],
            'elevation': [100, 150, 200],
            'slope': [5, 10, 15]
        })
        
        connector = FireSimulationConnector(grid_size=(20, 20))
        bounding_box = (127.0, 37.0, 127.4, 37.4)
        
        simulation_input = connector.create_simulation_input(
            forest_data, soil_data, elevation_data, bounding_box=bounding_box
        )
        
        print(f"  ✅ 시뮬레이션 입력 생성 성공")
        print(f"  📊 격자 크기: {simulation_input['grid_size']}")
        print(f"  🔥 연료 모델 종류: {np.unique(simulation_input['fuel_model'])}")
        print(f"  💧 수분 범위: {simulation_input['fuel_moisture'].min():.2f}-{simulation_input['fuel_moisture'].max():.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 시뮬레이션 연결기 테스트 실패: {e}")
        return False

def test_fire_model_integrator():
    """화재 모델 통합기 테스트 (더미 데이터)"""
    print("\n🎯 FireModelIntegrator 테스트 (더미 모드)...")
    
    try:
        from fire_model_integrator import FireModelIntegrator
        
        # 더미 데이터베이스 설정 (실제 연결하지 않음)
        db_config = {
            'host': 'localhost',
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_password',
            'port': 5432
        }
        
        # 작은 격자로 테스트
        simulation_config = {
            'grid_size': [10, 10],
            'simulation_steps': 5,
            'model_type': 'dummy',  # 더미 모드
            'wind_speed': 5.0,
            'output_dir': 'test_results'
        }
        
        integrator = FireModelIntegrator(db_config, simulation_config)
        
        print(f"  ✅ 통합기 초기화 성공")
        print(f"  📋 시뮬레이션 설정: {simulation_config['grid_size']} 격자")
        
        # 더미 시뮬레이션 테스트는 실제 DB 연결이 필요하므로 스킵
        print(f"  ⚠️ 실제 시뮬레이션은 PostgreSQL 연결 필요")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 화재 모델 통합기 테스트 실패: {e}")
        return False

def test_package_import():
    """패키지 전체 임포트 테스트"""
    print("\n📦 패키지 임포트 테스트...")
    
    try:
        import postgreSQLmodule
        print(f"  ✅ 패키지 임포트 성공")
        print(f"  📋 버전: {postgreSQLmodule.__version__}")
        print(f"  👨‍💻 개발자: {postgreSQLmodule.__author__}")
        
        # 개별 클래스 임포트 테스트
        from postgreSQLmodule import (
            SpatialDataExtractor,
            ForestDataProcessor, 
            SoilDataProcessor,
            FireSimulationConnector,
            FireModelIntegrator
        )
        
        print(f"  ✅ 모든 클래스 임포트 성공")
        return True
        
    except Exception as e:
        print(f"  ❌ 패키지 임포트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 PostgreSQL 화재 시뮬레이션 모듈 통합 테스트")
    print("=" * 60)
    
    test_results = []
    
    # 각 테스트 실행
    test_results.append(("모듈 임포트", test_module_imports()))
    test_results.append(("산림 처리기", test_forest_processor()))
    test_results.append(("토양 처리기", test_soil_processor()))
    test_results.append(("시뮬레이션 연결기", test_simulation_connector()))
    test_results.append(("화재 모델 통합기", test_fire_model_integrator()))
    test_results.append(("패키지 임포트", test_package_import()))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} : {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"총 테스트: {len(test_results)}")
    print(f"성공: {passed}")
    print(f"실패: {failed}")
    
    if failed == 0:
        print("\n🎉 모든 테스트 통과! 모듈이 올바르게 설정되었습니다.")
        print("\n💡 다음 단계:")
        print("   1. PostgreSQL/PostGIS 데이터베이스 설정")
        print("   2. 실제 공간 데이터 로드")
        print("   3. 화재 시뮬레이션 실행")
    else:
        print(f"\n⚠️ {failed}개 테스트 실패. 문제를 해결하고 다시 시도하세요.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
