#!/usr/bin/env python3
"""
화재 시뮬레이션 전용 로깅 및 모니터링 시스템
"""

import logging
import logging.handlers
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import queue
import traceback
import sys
import os
from contextlib import contextmanager


@dataclass
class LogEvent:
    """로그 이벤트"""
    timestamp: float
    level: str
    message: str
    module: str
    function: str
    line_number: int
    thread_id: int
    simulation_id: Optional[str] = None
    step: Optional[int] = None
    metadata: Dict[str, Any] = None


class FireSimulationLogger:
    """화재 시뮬레이션 전용 로거"""
    
    def __init__(self, name: str = "fire_simulation", 
                 log_dir: str = "logs",
                 level: str = "INFO"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 로거 설정
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 핸들러가 이미 있으면 제거 (중복 방지)
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 포매터 설정
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        
        # 핸들러 설정
        self._setup_handlers()
        
        # 이벤트 저장소
        self.events = deque(maxlen=10000)
        self.simulation_events = defaultdict(list)
        
        # 현재 시뮬레이션 컨텍스트
        self.current_simulation_id = None
        self.current_step = None
        
        # 통계
        self.stats = defaultdict(int)
        self.start_time = time.time()
    
    def _setup_handlers(self):
        """로그 핸들러 설정"""
        # 1. 파일 핸들러 (회전)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{self.name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
        
        # 2. 에러 전용 파일 핸들러
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{self.name}_errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.formatter)
        self.logger.addHandler(error_handler)
        
        # 3. 콘솔 핸들러
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(console_handler)
        
        # 4. JSON 구조화 로그 핸들러
        json_handler = logging.FileHandler(
            self.log_dir / f"{self.name}_structured.jsonl",
            encoding='utf-8'
        )
        json_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(json_handler)
    
    def set_simulation_context(self, simulation_id: str):
        """시뮬레이션 컨텍스트 설정"""
        self.current_simulation_id = simulation_id
        self.current_step = None
        self.info(f"시뮬레이션 시작: {simulation_id}")
    
    def set_step_context(self, step: int):
        """시뮬레이션 스텝 컨텍스트 설정"""
        self.current_step = step
    
    def clear_context(self):
        """컨텍스트 초기화"""
        if self.current_simulation_id:
            self.info(f"시뮬레이션 종료: {self.current_simulation_id}")
        self.current_simulation_id = None
        self.current_step = None
    
    def _log_with_context(self, level: str, message: str, **kwargs):
        """컨텍스트 정보와 함께 로깅"""
        # 호출자 정보 가져오기
        frame = sys._getframe(2)
        
        # 이벤트 생성
        event = LogEvent(
            timestamp=time.time(),
            level=level,
            message=message,
            module=frame.f_globals.get('__name__', 'unknown'),
            function=frame.f_code.co_name,
            line_number=frame.f_lineno,
            thread_id=threading.get_ident(),
            simulation_id=self.current_simulation_id,
            step=self.current_step,
            metadata=kwargs
        )
        
        # 이벤트 저장
        self.events.append(event)
        if self.current_simulation_id:
            self.simulation_events[self.current_simulation_id].append(event)
        
        # 통계 업데이트
        self.stats[level] += 1
        
        # 실제 로깅
        extra_info = ""
        if self.current_simulation_id:
            extra_info += f"[SIM:{self.current_simulation_id}]"
        if self.current_step is not None:
            extra_info += f"[STEP:{self.current_step}]"
        if kwargs:
            extra_info += f"[{', '.join(f'{k}={v}' for k, v in kwargs.items())}]"
        
        full_message = f"{extra_info} {message}" if extra_info else message
        
        getattr(self.logger, level.lower())(full_message)
    
    def debug(self, message: str, **kwargs):
        """디버그 로그"""
        self._log_with_context("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """정보 로그"""
        self._log_with_context("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """경고 로그"""
        self._log_with_context("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """에러 로그"""
        self._log_with_context("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """치명적 에러 로그"""
        self._log_with_context("CRITICAL", message, **kwargs)
    
    def log_performance(self, operation: str, duration: float, **metrics):
        """성능 로그"""
        self.info(f"Performance - {operation}", 
                 duration=duration, **metrics)
    
    def log_validation(self, metric_name: str, value: float, threshold: Optional[float] = None):
        """검증 메트릭 로그"""
        status = "PASS" if threshold and value >= threshold else "INFO"
        self.info(f"Validation - {metric_name}: {value:.3f}", 
                 metric=metric_name, value=value, threshold=threshold, status=status)
    
    def log_fire_event(self, event_type: str, location: tuple, **details):
        """화재 이벤트 로그"""
        self.info(f"Fire Event - {event_type} at {location}", 
                 event_type=event_type, location=location, **details)
    
    def log_exception(self, exc_info=None):
        """예외 로그"""
        if exc_info is None:
            exc_info = sys.exc_info()
        
        exc_type, exc_value, exc_traceback = exc_info
        if exc_type:
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.error(f"Exception: {exc_type.__name__}: {exc_value}")
            for line in tb_lines:
                self.debug(line.rstrip())
    
    @contextmanager
    def simulation_context(self, simulation_id: str):
        """시뮬레이션 컨텍스트 매니저"""
        self.set_simulation_context(simulation_id)
        try:
            yield self
        finally:
            self.clear_context()
    
    @contextmanager
    def step_context(self, step: int):
        """스텝 컨텍스트 매니저"""
        old_step = self.current_step
        self.set_step_context(step)
        try:
            yield self
        finally:
            self.current_step = old_step
    
    def get_simulation_summary(self, simulation_id: str) -> Dict[str, Any]:
        """시뮬레이션 요약 정보"""
        events = self.simulation_events.get(simulation_id, [])
        if not events:
            return {}
        
        # 레벨별 통계
        level_counts = defaultdict(int)
        for event in events:
            level_counts[event.level] += 1
        
        # 시간 정보
        start_time = min(event.timestamp for event in events)
        end_time = max(event.timestamp for event in events)
        duration = end_time - start_time
        
        # 스텝 정보
        steps = [event.step for event in events if event.step is not None]
        max_step = max(steps) if steps else 0
        
        return {
            'simulation_id': simulation_id,
            'total_events': len(events),
            'duration': duration,
            'max_step': max_step,
            'level_counts': dict(level_counts),
            'start_time': datetime.fromtimestamp(start_time).isoformat(),
            'end_time': datetime.fromtimestamp(end_time).isoformat()
        }
    
    def generate_report(self, output_path: str = None) -> Dict[str, Any]:
        """종합 로그 리포트 생성"""
        if output_path is None:
            output_path = self.log_dir / f"log_report_{int(time.time())}.json"
        
        # 전체 통계
        total_runtime = time.time() - self.start_time
        
        # 시뮬레이션별 요약
        simulation_summaries = {}
        for sim_id in self.simulation_events:
            simulation_summaries[sim_id] = self.get_simulation_summary(sim_id)
        
        # 최근 에러들
        recent_errors = [
            {
                'timestamp': datetime.fromtimestamp(event.timestamp).isoformat(),
                'message': event.message,
                'module': event.module,
                'function': event.function,
                'simulation_id': event.simulation_id,
                'step': event.step
            }
            for event in list(self.events)[-100:]  # 최근 100개
            if event.level in ['ERROR', 'CRITICAL']
        ]
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_runtime': total_runtime,
            'total_events': len(self.events),
            'level_statistics': dict(self.stats),
            'simulations': simulation_summaries,
            'recent_errors': recent_errors[-10:],  # 최근 10개 에러
            'log_files': [str(f) for f in self.log_dir.glob("*.log")]
        }
        
        # 파일로 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report


class JSONFormatter(logging.Formatter):
    """JSON 형식 로그 포매터"""
    
    def format(self, record):
        log_entry = {
            'timestamp': record.created,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread
        }
        
        # 추가 속성들
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'lineno', 
                          'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class LogAnalyzer:
    """로그 분석기"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
    
    def analyze_errors(self, hours: int = 24) -> Dict[str, Any]:
        """에러 분석"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        error_patterns = defaultdict(int)
        error_locations = defaultdict(int)
        
        # 에러 로그 파일 읽기
        error_log = self.log_dir / "fire_simulation_errors.log"
        if error_log.exists():
            with open(error_log, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'ERROR' in line or 'CRITICAL' in line:
                        # 간단한 패턴 분석
                        if 'Exception:' in line:
                            parts = line.split('Exception:')
                            if len(parts) > 1:
                                error_type = parts[1].split(':')[0].strip()
                                error_patterns[error_type] += 1
                        
                        # 위치 분석
                        if '[' in line and ']' in line:
                            location = line.split('[')[1].split(']')[0]
                            error_locations[location] += 1
        
        return {
            'analysis_period': f"{hours} hours",
            'total_errors': sum(error_patterns.values()),
            'error_patterns': dict(error_patterns),
            'error_locations': dict(error_locations)
        }
    
    def analyze_performance(self) -> Dict[str, Any]:
        """성능 분석"""
        performance_data = []
        
        # 구조화된 로그에서 성능 데이터 추출
        structured_log = self.log_dir / "fire_simulation_structured.jsonl"
        if structured_log.exists():
            with open(structured_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if 'Performance' in entry.get('message', ''):
                            performance_data.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        if not performance_data:
            return {'message': 'No performance data found'}
        
        # 성능 통계 계산
        durations = [entry.get('duration', 0) for entry in performance_data]
        
        return {
            'total_operations': len(performance_data),
            'average_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'recent_operations': performance_data[-10:]  # 최근 10개
        }


# 전역 로거 인스턴스
fire_logger = FireSimulationLogger()

# 편의 함수들
def get_logger() -> FireSimulationLogger:
    """전역 로거 반환"""
    return fire_logger

def log_simulation_start(simulation_id: str):
    """시뮬레이션 시작 로그"""
    fire_logger.set_simulation_context(simulation_id)

def log_simulation_end():
    """시뮬레이션 종료 로그"""
    fire_logger.clear_context()

def log_step(step: int):
    """스텝 설정"""
    fire_logger.set_step_context(step)

def log_performance(operation: str, duration: float, **metrics):
    """성능 로그"""
    fire_logger.log_performance(operation, duration, **metrics)

def log_fire_event(event_type: str, location: tuple, **details):
    """화재 이벤트 로그"""
    fire_logger.log_fire_event(event_type, location, **details)

def simulation_context(simulation_id: str):
    """시뮬레이션 컨텍스트 매니저"""
    return fire_logger.simulation_context(simulation_id)

def step_context(step: int):
    """스텝 컨텍스트 매니저"""
    return fire_logger.step_context(step)


if __name__ == '__main__':
    # 테스트 코드
    import argparse
    
    parser = argparse.ArgumentParser(description='로깅 시스템 테스트')
    parser.add_argument('--test', action='store_true', help='테스트 실행')
    parser.add_argument('--analyze', action='store_true', help='로그 분석')
    parser.add_argument('--report', action='store_true', help='리포트 생성')
    
    args = parser.parse_args()
    
    if args.test:
        print("로깅 시스템 테스트...")
        
        # 시뮬레이션 컨텍스트 테스트
        with simulation_context("test_simulation_001"):
            fire_logger.info("시뮬레이션 설정 완료")
            
            for step in range(5):
                with step_context(step):
                    fire_logger.debug(f"스텝 {step} 시작")
                    time.sleep(0.1)
                    
                    # 성능 로그
                    log_performance("step_execution", 0.1, 
                                  cells_processed=1000, 
                                  fire_cells=50)
                    
                    # 화재 이벤트
                    if step == 2:
                        log_fire_event("ignition", (25, 25), 
                                     intensity=100, fuel_type=8)
                    
                    fire_logger.info(f"스텝 {step} 완료")
            
            # 에러 테스트
            try:
                raise ValueError("테스트 에러")
            except Exception:
                fire_logger.log_exception()
        
        print("테스트 완료!")
    
    if args.analyze:
        analyzer = LogAnalyzer()
        
        print("에러 분석 결과:")
        error_analysis = analyzer.analyze_errors()
        print(json.dumps(error_analysis, indent=2, ensure_ascii=False))
        
        print("\n성능 분석 결과:")
        perf_analysis = analyzer.analyze_performance()
        print(json.dumps(perf_analysis, indent=2, ensure_ascii=False))
    
    if args.report:
        report = fire_logger.generate_report()
        print("로그 리포트 생성 완료!")
        print(f"총 이벤트: {report['total_events']}")
        print(f"실행 시간: {report['total_runtime']:.2f}초")
