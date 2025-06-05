"""
Configuration settings for the fire simulation visualization system.
"""

import os
import json
from typing import Dict, Any, Optional

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, 'postgreSQL', 'exports')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class VisualizationConfig:
    """시각화 설정 관리 클래스"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: 설정 파일 경로 (선택사항)
        """
        self.config_path = config_path
        self.config = self._load_default_config()
        
        if config_path and os.path.exists(config_path):
            self._load_config_file(config_path)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """기본 설정 로드"""
        return {
            'map': {
                'default_center': [37.5665, 126.9780],
                'default_zoom': 10,
                'tile_layer': 'OpenStreetMap',
                'max_zoom': 18,
                'min_zoom': 3,
                'attribution': 'Fire Simulation Visualization System'
            },
            'colors': {
                'fire_states': {
                    'empty': '#FFFFFF',
                    'fuel': '#228B22',
                    'burning': '#FF4500',
                    'burned': '#8B4513',
                    'water': '#4169E1'
                },
                'heat_map': {
                    'low': '#FFFF00',
                    'medium': '#FF8C00',
                    'high': '#FF0000'
                },
                'terrain': {
                    'contour_lines': '#8B4513',
                    'elevation_gradient': ['#90EE90', '#ADFF2F', '#32CD32', '#228B22', '#006400']
                }
            },
            'layers': {
                'fire_state': {
                    'enabled': True,
                    'opacity': 0.7,
                    'cell_size': 'auto'
                },
                'heat_map': {
                    'enabled': True,
                    'opacity': 0.6,
                    'radius': 15,
                    'blur': 15
                },
                'contour': {
                    'enabled': False,
                    'opacity': 0.5,
                    'line_weight': 2
                },
                'terrain': {
                    'enabled': False,
                    'opacity': 0.4
                }
            },
            'animation': {
                'interval': 1000,
                'auto_play': False,
                'loop': True,
                'show_controls': True
            },
            'charts': {
                'enable_3d': True,
                'color_scheme': 'viridis',
                'font_size': 12,
                'background_color': 'white'
            },
            'ui': {
                'theme': 'light',
                'sidebar_width': 300,
                'show_legend': True,
                'show_statistics': True
            },
            'output': {
                'directory': 'visualization_output',
                'format': 'html',
                'include_data': False
            },
            'performance': {
                'max_grid_size': 1000,
                'cache_enabled': True,
                'lazy_loading': True
            }
        }
    
    def _load_config_file(self, config_path: str):
        """설정 파일 로드 및 병합"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # 기본 설정과 파일 설정 병합
            self._merge_config(self.config, file_config)
            
        except Exception as e:
            print(f"설정 파일 로드 오류: {e}")
    
    def _merge_config(self, base: Dict, update: Dict):
        """재귀적 설정 병합"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key_path: str, default=None):
        """
        점 표기법으로 설정값 가져오기
        
        Args:
            key_path: 'map.default_center' 형식의 키 경로
            default: 기본값
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            return value
        except:
            return default
    
    def set(self, key_path: str, value):
        """
        점 표기법으로 설정값 저장
        
        Args:
            key_path: 'map.default_center' 형식의 키 경로
            value: 저장할 값
        """
        keys = key_path.split('.')
        target = self.config
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
    
    def save(self, output_path: Optional[str] = None):
        """설정을 파일로 저장"""
        if not output_path:
            output_path = self.config_path or 'config.json'
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"설정 저장 완료: {output_path}")
        except Exception as e:
            print(f"설정 저장 오류: {e}")


# Map configuration
MAP_CONFIG = {
    'default_center': [37.5665, 126.9780],  # Seoul coordinates as default
    'default_zoom': 10,
    'tile_layer': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}

# Fire visualization colors
FIRE_COLORS = {
    'empty': 'rgba(0, 0, 0, 0)',        # Transparent
    'tree': 'rgba(34, 139, 34, 0.6)',   # Forest green
    'burning': 'rgba(255, 69, 0, 0.8)',  # Red orange
    'burned': 'rgba(139, 69, 19, 0.7)',  # Saddle brown
    'wet': 'rgba(0, 191, 255, 0.6)'      # Deep sky blue
}

# Cell state mappings
CELL_STATES = {
    0: 'empty',
    1: 'tree', 
    2: 'burning',
    3: 'burned',
    4: 'wet'
}

# Animation settings
ANIMATION_CONFIG = {
    'default_speed': 500,  # milliseconds between frames
    'min_speed': 100,
    'max_speed': 2000,
    'auto_play': False
}

# Layer settings
LAYER_CONFIG = {
    'fire_grid': {
        'name': 'Fire Simulation',
        'opacity': 0.8,
        'z_index': 100
    },
    'heat_map': {
        'name': 'Heat Map',
        'opacity': 0.6,
        'z_index': 90
    },
    'terrain': {
        'name': 'Terrain',
        'opacity': 0.5,
        'z_index': 80
    },
    'fuel_types': {
        'name': 'Fuel Types',
        'opacity': 0.7,
        'z_index': 85
    }
}

# Chart settings
CHART_CONFIG = {
    'statistics': {
        'width': 400,
        'height': 300,
        'colors': {
            'empty_cells': '#ffffff',
            'tree_cells': '#228b22',
            'burning_cells': '#ff4500',
            'burned_cells': '#8b4513',
            'wet_cells': '#00bfff'
        }
    },
    'heat_evolution': {
        'width': 500,
        'height': 200,
        'color': '#ff6b35'
    }
}

# UI settings
UI_CONFIG = {
    'sidebar_width': 400,
    'control_panel_height': 150,
    'legend_height': 200
}

# Performance settings
PERFORMANCE_CONFIG = {
    'max_grid_size': 200,  # Maximum grid dimension for real-time rendering
    'chunk_size': 1000,    # Data processing chunk size
    'cache_size': 50       # Number of simulation steps to cache
}
