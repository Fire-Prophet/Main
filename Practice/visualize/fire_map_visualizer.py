"""
화재 지도 시각화의 메인 오케스트레이터 클래스
모든 컴포넌트를 통합하여 완전한 화재 시뮬레이션 시각화 시스템을 제공
"""

import os
import json
import folium
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path

from .config import VisualizationConfig
from .data_loader import SimulationDataLoader
from .layer_manager import LayerManager
from .map_renderer import MapRenderer
from .animation_controller import AnimationController
from .chart_generator import ChartGenerator
from .web_interface import WebInterface


class FireMapVisualizer:
    """
    화재 시뮬레이션 지도 시각화 메인 클래스
    모든 컴포넌트를 조합하여 완전한 시각화 시스템 제공
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: 설정 파일 경로 (선택사항)
        """
        self.config = VisualizationConfig(config_path)
        
        # 컴포넌트 초기화
        self.data_loader = SimulationDataLoader(self.config)
        self.layer_manager = LayerManager(self.config)
        self.map_renderer = MapRenderer(self.config)
        self.animation_controller = AnimationController(self.config)
        self.chart_generator = ChartGenerator(self.config)
        self.web_interface = WebInterface(self.config)
        
        # 데이터 저장
        self.simulation_data = None
        self.current_map = None
        self.current_step = 0
        
        # 결과 저장 디렉토리
        self.output_dir = Path(self.config.get('output', {}).get('directory', 'visualization_output'))
        self.output_dir.mkdir(exist_ok=True)
    
    def load_simulation_data(self, file_path: str) -> bool:
        """
        시뮬레이션 데이터 로드
        
        Args:
            file_path: 시뮬레이션 JSON 파일 경로
            
        Returns:
            bool: 로드 성공 여부
        """
        try:
            self.simulation_data = self.data_loader.load_simulation_data(file_path)
            
            if self.simulation_data:
                print(f"시뮬레이션 데이터 로드 완료: {len(self.simulation_data['steps'])} 스텝")
                
                # 다른 컴포넌트에 데이터 전달
                self.layer_manager.set_simulation_data(self.simulation_data)
                self.animation_controller.set_simulation_data(self.simulation_data)
                self.chart_generator.set_simulation_data(self.simulation_data)
                
                return True
            else:
                print("시뮬레이션 데이터 로드 실패")
                return False
                
        except Exception as e:
            print(f"데이터 로드 중 오류: {e}")
            return False
    
    def create_basic_map(self, step: int = 0) -> folium.Map:
        """
        기본 지도 생성
        
        Args:
            step: 표시할 시뮬레이션 스텝
            
        Returns:
            folium.Map: 생성된 지도 객체
        """
        if not self.simulation_data:
            raise ValueError("시뮬레이션 데이터가 로드되지 않았습니다.")
        
        # 지도 생성
        bounds = self.simulation_data.get('geographic_bounds')
        if bounds:
            center_lat = (bounds['min_lat'] + bounds['max_lat']) / 2
            center_lon = (bounds['min_lon'] + bounds['max_lon']) / 2
        else:
            center_lat = self.config.get('map', {}).get('default_center', [37.5665, 126.9780])[0]
            center_lon = self.config.get('map', {}).get('default_center', [37.5665, 126.9780])[1]
        
        self.current_map = self.map_renderer.create_base_map(
            center=[center_lat, center_lon],
            bounds=bounds
        )
        
        # 화재 상태 레이어 추가
        if step < len(self.simulation_data['steps']):
            step_data = self.simulation_data['steps'][step]
            
            # 화재 상태 레이어
            fire_layer = self.layer_manager.create_fire_state_layer(step_data)
            fire_layer.add_to(self.current_map)
            
            # 열 지도 레이어 (선택적)
            if self.config.get('layers', {}).get('heat_map', {}).get('enabled', True):
                heat_layer = self.layer_manager.create_heat_map_layer(step_data)
                heat_layer.add_to(self.current_map)
            
            # 등고선 레이어 (지형 데이터가 있는 경우)
            if 'terrain' in self.simulation_data:
                contour_layer = self.layer_manager.create_contour_layer(
                    self.simulation_data['terrain']
                )
                contour_layer.add_to(self.current_map)
        
        # 레이어 컨트롤 추가
        folium.LayerControl().add_to(self.current_map)
        
        self.current_step = step
        return self.current_map
    
    def create_interactive_map(self, include_timeline: bool = True) -> folium.Map:
        """
        상호작용 가능한 지도 생성 (타임라인 포함)
        
        Args:
            include_timeline: 타임라인 컨트롤 포함 여부
            
        Returns:
            folium.Map: 상호작용 지도 객체
        """
        if not self.simulation_data:
            raise ValueError("시뮬레이션 데이터가 로드되지 않았습니다.")
        
        # 기본 지도 생성
        self.create_basic_map(0)
        
        # 모든 스텝의 레이어 생성
        all_layers = []
        for i, step_data in enumerate(self.simulation_data['steps']):
            layer_group = folium.FeatureGroup(name=f'Step {i}')
            
            # 화재 상태 레이어
            fire_layer = self.layer_manager.create_fire_state_layer(step_data)
            fire_layer.add_to(layer_group)
            
            all_layers.append(layer_group)
        
        # 타임라인 컨트롤 추가
        if include_timeline:
            timeline_control = self.animation_controller.create_timeline_control(all_layers)
            timeline_control.add_to(self.current_map)
        
        return self.current_map
    
    def create_animation(self, output_path: Optional[str] = None) -> str:
        """
        화재 진행 애니메이션 생성
        
        Args:
            output_path: 출력 파일 경로
            
        Returns:
            str: 생성된 애니메이션 파일 경로
        """
        if not self.simulation_data:
            raise ValueError("시뮬레이션 데이터가 로드되지 않았습니다.")
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"fire_animation_{timestamp}.html"
        
        # 애니메이션 생성
        animation_map = self.animation_controller.create_step_animation(
            self.simulation_data['steps']
        )
        
        # 저장
        animation_map.save(str(output_path))
        print(f"애니메이션 저장 완료: {output_path}")
        
        return str(output_path)
    
    def generate_comprehensive_charts(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        종합적인 차트 세트 생성
        
        Args:
            output_dir: 출력 디렉토리
            
        Returns:
            Dict[str, str]: 생성된 차트 파일 경로들
        """
        if not self.simulation_data:
            raise ValueError("시뮬레이션 데이터가 로드되지 않았습니다.")
        
        if not output_dir:
            output_dir = self.output_dir / "charts"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        chart_paths = {}
        
        # 시간 진행 차트
        evolution_fig = self.chart_generator.create_time_evolution_chart()
        evolution_path = output_dir / "time_evolution.html"
        evolution_fig.write_html(str(evolution_path))
        chart_paths['time_evolution'] = str(evolution_path)
        
        # 화재 강도 히트맵
        heatmap_fig = self.chart_generator.create_fire_intensity_heatmap()
        heatmap_path = output_dir / "fire_intensity_heatmap.html"
        heatmap_fig.write_html(str(heatmap_path))
        chart_paths['fire_intensity'] = str(heatmap_path)
        
        # 연소 비율 차트
        burn_ratio_fig = self.chart_generator.create_burn_ratio_chart()
        burn_ratio_path = output_dir / "burn_ratio.html"
        burn_ratio_fig.write_html(str(burn_ratio_path))
        chart_paths['burn_ratio'] = str(burn_ratio_path)
        
        # 3D 시각화
        if self.config.get('charts', {}).get('enable_3d', True):
            viz_3d_fig = self.chart_generator.create_3d_visualization()
            viz_3d_path = output_dir / "3d_visualization.html"
            viz_3d_fig.write_html(str(viz_3d_path))
            chart_paths['3d_visualization'] = str(viz_3d_path)
        
        print(f"차트 생성 완료: {len(chart_paths)}개 파일")
        return chart_paths
    
    def create_comprehensive_report(self, output_path: Optional[str] = None) -> str:
        """
        종합 보고서 생성 (지도, 차트, 통계 포함)
        
        Args:
            output_path: 보고서 출력 경로
            
        Returns:
            str: 생성된 보고서 파일 경로
        """
        if not self.simulation_data:
            raise ValueError("시뮬레이션 데이터가 로드되지 않았습니다.")
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"fire_simulation_report_{timestamp}.html"
        
        # 지도 생성
        final_step = len(self.simulation_data['steps']) - 1
        report_map = self.create_basic_map(final_step)
        
        # 차트 생성
        chart_paths = self.generate_comprehensive_charts()
        
        # HTML 보고서 생성
        html_content = self._generate_html_report(report_map, chart_paths)
        
        # 파일 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"종합 보고서 생성 완료: {output_path}")
        return str(output_path)
    
    def launch_web_interface(self, port: int = 8501) -> None:
        """
        웹 인터페이스 실행
        
        Args:
            port: 웹 서버 포트
        """
        if not self.simulation_data:
            print("경고: 시뮬레이션 데이터가 로드되지 않았습니다.")
        
        # 웹 인터페이스 컴포넌트에 필요한 객체들 전달
        self.web_interface.set_components(
            visualizer=self,
            data_loader=self.data_loader,
            layer_manager=self.layer_manager,
            map_renderer=self.map_renderer,
            animation_controller=self.animation_controller,
            chart_generator=self.chart_generator
        )
        
        # Streamlit 앱 실행
        self.web_interface.run_streamlit_app(port)
    
    def export_data(self, format: str = 'json', output_path: Optional[str] = None) -> str:
        """
        시각화 데이터 내보내기
        
        Args:
            format: 내보내기 형식 ('json', 'geojson', 'csv')
            output_path: 출력 파일 경로
            
        Returns:
            str: 내보낸 파일 경로
        """
        if not self.simulation_data:
            raise ValueError("시뮬레이션 데이터가 로드되지 않았습니다.")
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"exported_data_{timestamp}.{format}"
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.simulation_data, f, indent=2, ensure_ascii=False)
        
        elif format == 'geojson':
            geojson_data = self._convert_to_geojson()
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(geojson_data, f, indent=2)
        
        elif format == 'csv':
            import pandas as pd
            df = self._convert_to_dataframe()
            df.to_csv(output_path, index=False)
        
        else:
            raise ValueError(f"지원하지 않는 형식: {format}")
        
        print(f"데이터 내보내기 완료: {output_path}")
        return str(output_path)
    
    def get_simulation_statistics(self) -> Dict[str, Any]:
        """
        시뮬레이션 통계 정보 반환
        
        Returns:
            Dict[str, Any]: 통계 정보
        """
        if not self.simulation_data:
            return {}
        
        steps = self.simulation_data['steps']
        total_cells = steps[0]['grid_shape'][0] * steps[0]['grid_shape'][1]
        
        stats = {
            'total_steps': len(steps),
            'total_cells': total_cells,
            'max_burning_cells': max(step['stats']['burning_cells'] for step in steps),
            'final_burn_ratio': steps[-1]['stats']['burn_ratio'],
            'simulation_duration': len(steps),
            'grid_dimensions': steps[0]['grid_shape']
        }
        
        # 각 스텝별 통계
        step_stats = []
        for i, step in enumerate(steps):
            step_stat = {
                'step': i,
                'burning_cells': step['stats']['burning_cells'],
                'burned_cells': step['stats']['burned_cells'],
                'burn_ratio': step['stats']['burn_ratio']
            }
            step_stats.append(step_stat)
        
        stats['step_statistics'] = step_stats
        
        return stats
    
    def _generate_html_report(self, map_obj: folium.Map, chart_paths: Dict[str, str]) -> str:
        """HTML 보고서 생성"""
        map_html = map_obj._repr_html_()
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>화재 시뮬레이션 보고서</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin: 30px 0; }}
                .map-container {{ width: 100%; height: 600px; }}
                .chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                .chart-item {{ border: 1px solid #ddd; padding: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>화재 시뮬레이션 시각화 보고서</h1>
                <p>생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>최종 화재 확산 지도</h2>
                <div class="map-container">
                    {map_html}
                </div>
            </div>
            
            <div class="section">
                <h2>분석 차트</h2>
                <div class="chart-grid">
                    <div class="chart-item">
                        <h3>시간별 진행</h3>
                        <iframe src="{chart_paths.get('time_evolution', '')}" width="100%" height="400px"></iframe>
                    </div>
                    <div class="chart-item">
                        <h3>화재 강도 분포</h3>
                        <iframe src="{chart_paths.get('fire_intensity', '')}" width="100%" height="400px"></iframe>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _convert_to_geojson(self) -> Dict:
        """시뮬레이션 데이터를 GeoJSON으로 변환"""
        features = []
        
        for step_idx, step_data in enumerate(self.simulation_data['steps']):
            grid = np.array(step_data['grid'])
            bounds = self.simulation_data.get('geographic_bounds')
            
            if bounds:
                # 격자 셀을 GeoJSON 피처로 변환
                for i in range(grid.shape[0]):
                    for j in range(grid.shape[1]):
                        if grid[i, j] > 0:  # 빈 셀이 아닌 경우만
                            # 격자 좌표를 지리적 좌표로 변환
                            lat_step = (bounds['max_lat'] - bounds['min_lat']) / grid.shape[0]
                            lon_step = (bounds['max_lon'] - bounds['min_lon']) / grid.shape[1]
                            
                            lat = bounds['min_lat'] + i * lat_step
                            lon = bounds['min_lon'] + j * lon_step
                            
                            feature = {
                                "type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [lon, lat]
                                },
                                "properties": {
                                    "step": step_idx,
                                    "state": int(grid[i, j]),
                                    "grid_i": i,
                                    "grid_j": j
                                }
                            }
                            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def _convert_to_dataframe(self):
        """시뮬레이션 데이터를 DataFrame으로 변환"""
        import pandas as pd
        
        rows = []
        for step_idx, step_data in enumerate(self.simulation_data['steps']):
            grid = np.array(step_data['grid'])
            
            for i in range(grid.shape[0]):
                for j in range(grid.shape[1]):
                    row = {
                        'step': step_idx,
                        'grid_i': i,
                        'grid_j': j,
                        'state': int(grid[i, j])
                    }
                    rows.append(row)
        
        return pd.DataFrame(rows)


def main():
    """메인 실행 함수 - 데모용"""
    import argparse
    
    parser = argparse.ArgumentParser(description='화재 시뮬레이션 지도 시각화')
    parser.add_argument('--data', type=str, required=True, help='시뮬레이션 JSON 데이터 파일')
    parser.add_argument('--output', type=str, help='출력 디렉토리')
    parser.add_argument('--web', action='store_true', help='웹 인터페이스 실행')
    parser.add_argument('--report', action='store_true', help='종합 보고서 생성')
    parser.add_argument('--animation', action='store_true', help='애니메이션 생성')
    
    args = parser.parse_args()
    
    # 시각화 시스템 초기화
    visualizer = FireMapVisualizer()
    
    # 데이터 로드
    if not visualizer.load_simulation_data(args.data):
        print("데이터 로드 실패")
        return
    
    # 출력 디렉토리 설정
    if args.output:
        visualizer.output_dir = Path(args.output)
        visualizer.output_dir.mkdir(exist_ok=True)
    
    # 웹 인터페이스 실행
    if args.web:
        visualizer.launch_web_interface()
        return
    
    # 종합 보고서 생성
    if args.report:
        report_path = visualizer.create_comprehensive_report()
        print(f"보고서 생성 완료: {report_path}")
    
    # 애니메이션 생성
    if args.animation:
        animation_path = visualizer.create_animation()
        print(f"애니메이션 생성 완료: {animation_path}")
    
    # 기본 지도 생성
    if not args.report and not args.animation:
        map_obj = visualizer.create_basic_map()
        output_path = visualizer.output_dir / "fire_map.html"
        map_obj.save(str(output_path))
        print(f"기본 지도 저장 완료: {output_path}")


if __name__ == "__main__":
    main()
