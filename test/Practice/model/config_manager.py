#!/usr/bin/env python3
"""
화재 시뮬레이션 환경 설정 관리자
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv


@dataclass
class SimulationConfig:
    """시뮬레이션 기본 설정"""
    grid_size: tuple = (100, 100)
    cell_size: float = 30.0
    max_steps: int = 100
    validation_interval: int = 10
    save_intermediate: bool = True
    

@dataclass
class PerformanceConfig:
    """성능 설정"""
    num_threads: int = 4
    use_gpu: bool = False
    memory_limit: str = "8GB"
    batch_size: int = 1000
    enable_caching: bool = True
    

@dataclass
class VisualizationConfig:
    """시각화 설정"""
    backend: str = "matplotlib"
    figure_dpi: int = 300
    animation_fps: int = 10
    color_scheme: str = "viridis"
    save_format: str = "png"
    

@dataclass
class LoggingConfig:
    """로깅 설정"""
    level: str = "INFO"
    file_path: str = "logs/simulation.log"
    max_size: str = "100MB"
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class ConfigManager:
    """설정 관리자"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yaml"
        self.env_file = ".env"
        
        # 환경 변수 로드
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
        
        # 기본 설정
        self.simulation = SimulationConfig()
        self.performance = PerformanceConfig()
        self.visualization = VisualizationConfig()
        self.logging = LoggingConfig()
        
        # 설정 파일에서 로드
        self.load_config()
        
        # 환경 변수로 오버라이드
        self.load_from_env()
    
    def load_config(self):
        """설정 파일에서 설정 로드"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            
            # 설정 적용
            if 'simulation' in config:
                self.simulation = SimulationConfig(**config['simulation'])
            if 'performance' in config:
                self.performance = PerformanceConfig(**config['performance'])
            if 'visualization' in config:
                self.visualization = VisualizationConfig(**config['visualization'])
            if 'logging' in config:
                self.logging = LoggingConfig(**config['logging'])
    
    def load_from_env(self):
        """환경 변수에서 설정 로드"""
        # 시뮬레이션 설정
        if grid_size := os.getenv('FIRE_SIM_DEFAULT_GRID_SIZE'):
            try:
                w, h = map(int, grid_size.split(','))
                self.simulation.grid_size = (w, h)
            except ValueError:
                pass
        
        if cell_size := os.getenv('FIRE_SIM_DEFAULT_CELL_SIZE'):
            try:
                self.simulation.cell_size = float(cell_size)
            except ValueError:
                pass
        
        if max_steps := os.getenv('FIRE_SIM_DEFAULT_MAX_STEPS'):
            try:
                self.simulation.max_steps = int(max_steps)
            except ValueError:
                pass
        
        # 성능 설정
        if num_threads := os.getenv('FIRE_SIM_NUM_THREADS'):
            try:
                self.performance.num_threads = int(num_threads)
            except ValueError:
                pass
        
        if use_gpu := os.getenv('FIRE_SIM_USE_GPU'):
            self.performance.use_gpu = use_gpu.lower() == 'true'
        
        if memory_limit := os.getenv('FIRE_SIM_MEMORY_LIMIT'):
            self.performance.memory_limit = memory_limit
        
        # 시각화 설정
        if backend := os.getenv('FIRE_SIM_PLOT_BACKEND'):
            self.visualization.backend = backend
        
        if fps := os.getenv('FIRE_SIM_ANIMATION_FPS'):
            try:
                self.visualization.animation_fps = int(fps)
            except ValueError:
                pass
        
        if dpi := os.getenv('FIRE_SIM_FIGURE_DPI'):
            try:
                self.visualization.figure_dpi = int(dpi)
            except ValueError:
                pass
        
        # 로깅 설정
        if log_level := os.getenv('FIRE_SIM_LOG_LEVEL'):
            self.logging.level = log_level.upper()
        
        if log_file := os.getenv('FIRE_SIM_LOG_FILE'):
            self.logging.file_path = log_file
    
    def save_config(self, path: Optional[str] = None):
        """설정을 파일로 저장"""
        save_path = path or self.config_path
        
        config = {
            'simulation': asdict(self.simulation),
            'performance': asdict(self.performance),
            'visualization': asdict(self.visualization),
            'logging': asdict(self.logging)
        }
        
        with open(save_path, 'w', encoding='utf-8') as f:
            if save_path.endswith('.yaml') or save_path.endswith('.yml'):
                yaml.dump(config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            else:
                json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get_all_config(self) -> Dict[str, Any]:
        """모든 설정을 딕셔너리로 반환"""
        return {
            'simulation': asdict(self.simulation),
            'performance': asdict(self.performance),
            'visualization': asdict(self.visualization),
            'logging': asdict(self.logging)
        }
    
    def create_directories(self):
        """필요한 디렉토리 생성"""
        directories = [
            os.getenv('FIRE_SIM_DATA_DIR', 'data'),
            os.getenv('FIRE_SIM_RESULTS_DIR', 'results'),
            os.getenv('FIRE_SIM_CACHE_DIR', '.cache'),
            os.path.dirname(self.logging.file_path)
        ]
        
        for directory in directories:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """로깅 설정"""
        import logging
        from logging.handlers import RotatingFileHandler
        
        # 디렉토리 생성
        log_dir = os.path.dirname(self.logging.file_path)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # 로거 설정
        logger = logging.getLogger('fire_simulation')
        logger.setLevel(getattr(logging, self.logging.level))
        
        # 파일 핸들러
        if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
            file_handler = RotatingFileHandler(
                self.logging.file_path,
                maxBytes=self._parse_size(self.logging.max_size),
                backupCount=self.logging.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(logging.Formatter(self.logging.format))
            logger.addHandler(file_handler)
        
        # 콘솔 핸들러
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(self.logging.format))
            logger.addHandler(console_handler)
        
        return logger
    
    def _parse_size(self, size_str: str) -> int:
        """크기 문자열을 바이트로 변환"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def print_config(self):
        """현재 설정 출력"""
        print("🔥 Fire Simulation Configuration")
        print("=" * 50)
        
        print("\n📊 Simulation:")
        print(f"  Grid Size: {self.simulation.grid_size}")
        print(f"  Cell Size: {self.simulation.cell_size}m")
        print(f"  Max Steps: {self.simulation.max_steps}")
        
        print("\n⚡ Performance:")
        print(f"  Threads: {self.performance.num_threads}")
        print(f"  GPU: {'Enabled' if self.performance.use_gpu else 'Disabled'}")
        print(f"  Memory Limit: {self.performance.memory_limit}")
        
        print("\n🎨 Visualization:")
        print(f"  Backend: {self.visualization.backend}")
        print(f"  DPI: {self.visualization.figure_dpi}")
        print(f"  Animation FPS: {self.visualization.animation_fps}")
        
        print("\n📝 Logging:")
        print(f"  Level: {self.logging.level}")
        print(f"  File: {self.logging.file_path}")


def create_default_config():
    """기본 설정 파일 생성"""
    config_manager = ConfigManager()
    config_manager.save_config("config.yaml")
    print("기본 설정 파일 'config.yaml'이 생성되었습니다.")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='화재 시뮬레이션 설정 관리')
    parser.add_argument('--create-default', action='store_true', 
                       help='기본 설정 파일 생성')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='설정 파일 경로')
    parser.add_argument('--print', action='store_true',
                       help='현재 설정 출력')
    
    args = parser.parse_args()
    
    if args.create_default:
        create_default_config()
    
    if args.print:
        config_manager = ConfigManager(args.config)
        config_manager.print_config()
