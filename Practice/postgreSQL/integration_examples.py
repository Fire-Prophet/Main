#!/usr/bin/env python3
"""
PostgreSQL과 화재 모델 연동 사용 예제
실제 연동 방법과 사용 패턴을 보여주는 예제 코드
"""

import numpy as np
from model_integration import PostgreSQLModelIntegrator
from pathlib import Path

def example_basic_integration():
    """기본 연동 예제"""
    print("=== 기본 PostgreSQL ↔ 화재 모델 연동 ===")
    
    integrator = PostgreSQLModelIntegrator()
    
    if not integrator.connect():
        print("❌ 데이터베이스 연결 실패!")
        return
    
    try:
        # 1. 공간 테이블 확인
        print("\n1. 공간 테이블 조회:")
        spatial_tables = integrator.get_spatial_tables()
        
        for table in spatial_tables[:3]:  # 처음 3개만 표시
            print(f"   📊 {table['table_name']}: {table['geometry_type']} (SRID: {table['srid']})")
        
        if not spatial_tables:
            print("   ⚠️  공간 테이블이 없습니다.")
            return
        
        # 2. 첫 번째 테이블로 연료 데이터 추출 테스트
        test_table = spatial_tables[0]['table_name']
        geom_column = spatial_tables[0]['geom_column']
        
        print(f"\n2. '{test_table}' 테이블에서 연료 데이터 추출:")
        
        fuel_grid = integrator.extract_fuel_data_from_postgis(
            test_table, 
            geom_column,
            grid_size=(10, 10)  # 작은 테스트 격자
        )
        
        print(f"   연료 격자 크기: {fuel_grid.shape}")
        print(f"   연료 타입: {np.unique(fuel_grid)}")
        print(f"   샘플 격자:")
        print(f"   {fuel_grid[:3, :3]}")
        
        # 3. 화재 시뮬레이션 모델 생성 (model 디렉토리가 있는 경우)
        print(f"\n3. 화재 시뮬레이션 모델 생성:")
        
        fire_model = integrator.create_fire_simulation_from_postgis(
            test_table,
            grid_size=(20, 20),
            ignition_points=[(10, 10)],
            simulation_config={
                'tree_density': 0.8,
                'base_spread_prob': 0.2
            }
        )
        
        if fire_model:
            print("   ✅ 화재 모델 생성 성공!")
            
            # 간단한 시뮬레이션 실행
            print("\n4. 시뮬레이션 실행 (10 스텝):")
            for step in range(10):
                stats = fire_model.step()
                if step % 3 == 0:
                    print(f"      Step {step}: 연소중 {stats.get('burning_cells', 0)}, "
                          f"연소완료 {stats.get('burned_cells', 0)}")
        
        print("\n✅ 기본 연동 테스트 완료!")
        
    finally:
        integrator.disconnect()

def example_data_export_for_model():
    """모델 입력용 데이터 내보내기 예제"""
    print("\n=== 모델 입력용 데이터 내보내기 ===")
    
    integrator = PostgreSQLModelIntegrator()
    
    if not integrator.connect():
        return
    
    try:
        # CSV 형태로 공간 데이터 내보내기
        exporter = integrator.exporter
        
        # 공간 테이블 찾기
        spatial_tables = integrator.get_spatial_tables()
        if spatial_tables:
            table_name = spatial_tables[0]['table_name']
            
            print(f"📁 '{table_name}' 테이블 데이터 내보내기:")
            
            # CSV로 내보내기
            csv_file = exporter.export_table_to_csv(table_name, limit=100)
            if csv_file:
                print(f"   ✅ CSV 파일: {csv_file}")
            
            # GeoJSON으로 내보내기 (공간 데이터)
            geom_column = spatial_tables[0]['geom_column']
            geojson_file = exporter.export_spatial_data_to_geojson(
                table_name, geom_column, limit=50
            )
            if geojson_file:
                print(f"   ✅ GeoJSON 파일: {geojson_file}")
        
    finally:
        integrator.disconnect()

def example_custom_fuel_mapping():
    """사용자 정의 연료 매핑 예제"""
    print("\n=== 사용자 정의 연료 매핑 ===")
    
    # 연료 매핑 함수 예제
    def custom_fuel_mapper(raw_fuel_value):
        """
        실제 데이터의 연료 값을 Anderson13 연료 모델로 매핑하는 사용자 정의 함수
        """
        if raw_fuel_value is None:
            return 'NB1'  # 비연소성
        
        fuel_str = str(raw_fuel_value).upper()
        
        # 예: 한국 산림청 임상도 분류
        if 'PINE' in fuel_str or '소나무' in fuel_str:
            return 'TL2'  # 소나무림
        elif 'OAK' in fuel_str or '참나무' in fuel_str:
            return 'TU2'  # 참나무림
        elif 'MIXED' in fuel_str or '혼효' in fuel_str:
            return 'TU3'  # 혼효림
        elif 'BAMBOO' in fuel_str or '대나무' in fuel_str:
            return 'GR1'  # 대나무(초지류)
        else:
            return 'TL1'  # 기본 침엽수
    
    # 사용자 정의 매핑을 적용한 연료 추출
    print("   사용자 정의 연료 매핑 규칙:")
    test_values = ['PINE_FOREST', '소나무림', 'OAK_FOREST', 'MIXED_FOREST', None, 'UNKNOWN']
    
    for value in test_values:
        mapped = custom_fuel_mapper(value)
        print(f"      '{value}' → '{mapped}'")

def example_simulation_with_real_data():
    """실제 데이터를 이용한 시뮬레이션 예제"""
    print("\n=== 실제 데이터 기반 화재 시뮬레이션 ===")
    
    integrator = PostgreSQLModelIntegrator()
    
    if not integrator.connect():
        return
    
    try:
        # 실제 공간 테이블 선택
        spatial_tables = integrator.get_spatial_tables()
        
        if not spatial_tables:
            print("   ⚠️  공간 테이블이 없어 예제를 실행할 수 없습니다.")
            return
        
        # 첫 번째 테이블로 시뮬레이션
        table_name = spatial_tables[0]['table_name']
        print(f"   데이터 소스: {table_name}")
        
        # 시뮬레이션 설정
        config = {
            'grid_size': (50, 50),
            'ignition_points': [(25, 25), (15, 35)],  # 다중 점화점
            'simulation_config': {
                'tree_density': 0.75,
                'base_spread_prob': 0.18,
                'ignition_prob': 0.002,
                'extinguish_prob': 0.06
            },
            'steps': 30
        }
        
        print(f"   격자 크기: {config['grid_size']}")
        print(f"   점화점: {config['ignition_points']}")
        print(f"   시뮬레이션 스텝: {config['steps']}")
        
        # 시뮬레이션 실행
        result = integrator.run_integrated_simulation(
            table_name, 
            steps=config['steps']
        )
        
        if result['success']:
            final_stats = result['results']['final_stats']
            print(f"\n📊 시뮬레이션 결과:")
            print(f"   총 스텝: {len(result['results']['steps'])}")
            print(f"   최종 연소 셀: {final_stats['burned_cells']}")
            print(f"   연소율: {final_stats['burn_ratio']:.1%}")
            print(f"   화재 둘레: {final_stats['fire_perimeter']}")
            
            # 연소 패턴 분석
            burned_over_time = [stat['burned_cells'] for stat in result['results']['statistics']]
            if len(burned_over_time) > 1:
                max_spread_rate = max(burned_over_time[i] - burned_over_time[i-1] 
                                    for i in range(1, len(burned_over_time)))
                print(f"   최대 확산 속도: {max_spread_rate} 셀/스텝")
        
    finally:
        integrator.disconnect()

def example_data_preprocessing():
    """데이터 전처리 예제"""
    print("\n=== 데이터 전처리 및 품질 확인 ===")
    
    integrator = PostgreSQLModelIntegrator()
    
    if not integrator.connect():
        return
    
    try:
        # 테이블 품질 분석
        from data_quality_checker import PostgreSQLDataQualityChecker
        
        quality_checker = PostgreSQLDataQualityChecker()
        quality_checker.db = integrator.db
        
        spatial_tables = integrator.get_spatial_tables()
        
        if spatial_tables:
            table_name = spatial_tables[0]['table_name']
            print(f"📊 '{table_name}' 테이블 품질 분석:")
            
            # 기본 품질 체크
            quality_results = quality_checker.comprehensive_quality_check(table_name)
            
            # 안전한 결과 출력
            if 'null_analysis' in quality_results:
                print(f"   NULL 값 품질: {quality_results['null_analysis'].get('quality_score', 0):.1f}/100")
            
            if 'consistency_analysis' in quality_results:
                print(f"   데이터 일관성: {quality_results['consistency_analysis'].get('quality_score', 0):.1f}/100")
            
            if 'overall_quality' in quality_results:
                print(f"   전체 품질 등급: {quality_results['overall_quality'].get('grade', '알 수 없음')}")
            else:
                print(f"   품질 분석 완료: {len(quality_results)} 개 항목 검사됨")
            
            # 공간 데이터 특화 체크
            analyzer = integrator.analyzer
            spatial_info = analyzer.get_spatial_info(table_name)
            
            if spatial_info:
                geom_column = spatial_info[0]['geom_column']
                extent = analyzer.get_spatial_extent(table_name, geom_column)
                
                if extent:
                    ext = extent[0]
                    print(f"\n🌍 공간 데이터 정보:")
                    print(f"   공간 범위: X({ext['min_x']:.2f}~{ext['max_x']:.2f}), "
                          f"Y({ext['min_y']:.2f}~{ext['max_y']:.2f})")
                    print(f"   총 피처 수: {ext['geom_count']:,}")
                    print(f"   유효 지오메트리: {ext['valid_geom_count']:,}")
                    
                    # 공간 데이터 품질 평가
                    validity_ratio = ext['valid_geom_count'] / ext['geom_count'] if ext['geom_count'] > 0 else 0
                    print(f"   지오메트리 유효율: {validity_ratio:.1%}")
        
    except ImportError:
        print("   ⚠️  품질 검사 모듈을 사용할 수 없습니다.")
    
    finally:
        integrator.disconnect()

def show_integration_capabilities():
    """연동 가능한 기능 목록 표시"""
    print("\n" + "="*70)
    print("🔥 PostgreSQL ↔ 화재 모델 연동 기능")
    print("="*70)
    
    print("\n📊 데이터 추출 기능:")
    print("   • PostGIS 공간 데이터 → 연료 격자 변환")
    print("   • 지형 데이터 (고도, 경사) 추출")
    print("   • 기상 관측 데이터 추출 (테이블이 있는 경우)")
    print("   • 도로/수계 등 인프라 데이터 추출")
    
    print("\n🔥 모델 연동 기능:")
    print("   • AdvancedCAModel 자동 설정")
    print("   • RealisticFireModel 데이터 연결")
    print("   • IntegratedFireSimulation 파이프라인")
    print("   • 사용자 정의 연료 매핑")
    
    print("\n📁 데이터 형식 지원:")
    print("   • CSV (범용 데이터)")
    print("   • JSON (구조화 데이터)")
    print("   • GeoJSON (공간 데이터)")
    print("   • NumPy 배열 (직접 연동)")
    
    print("\n🚀 시뮬레이션 기능:")
    print("   • 실시간 데이터 기반 시뮬레이션")
    print("   • 다중 점화점 시나리오")
    print("   • 결과 자동 저장 및 분석")
    print("   • 성능 통계 모니터링")
    
    print("\n💡 활용 시나리오:")
    print("   • 실제 산림 데이터 기반 화재 위험도 평가")
    print("   • 화재 진압 계획 수립을 위한 시뮬레이션")
    print("   • 기상 조건 변화에 따른 확산 예측")
    print("   • 방화선 효과 검증")

def main():
    """메인 함수 - 모든 예제 실행"""
    print("🔥 PostgreSQL과 화재 모델 연동 예제 모음")
    
    show_integration_capabilities()
    
    # 사용자 선택 메뉴
    while True:
        print("\n" + "-"*50)
        print("📚 실행할 예제를 선택하세요:")
        print("1. 기본 연동 테스트")
        print("2. 데이터 내보내기")
        print("3. 사용자 정의 연료 매핑")
        print("4. 실제 데이터 시뮬레이션")
        print("5. 데이터 전처리 및 품질 확인")
        print("6. 전체 연동 인터페이스 실행")
        print("0. 종료")
        
        choice = input("\n선택 (0-6): ").strip()
        
        if choice == '0':
            print("👋 종료합니다.")
            break
        elif choice == '1':
            example_basic_integration()
        elif choice == '2':
            example_data_export_for_model()
        elif choice == '3':
            example_custom_fuel_mapping()
        elif choice == '4':
            example_simulation_with_real_data()
        elif choice == '5':
            example_data_preprocessing()
        elif choice == '6':
            # 전체 통합 인터페이스 실행
            integrator = PostgreSQLModelIntegrator()
            integrator.interactive_menu()
        else:
            print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main()
