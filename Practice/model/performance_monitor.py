#!/usr/bin/env python3
"""
화재 시뮬레이션 성능 모니터링 및 프로파일링 도구
"""

import time
import psutil
import gc
import threading
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json


@dataclass
class PerformanceMetrics:
    """성능 메트릭스"""
    name: str
    start_time: float
    end_time: float
    duration: float
    memory_before: float
    memory_after: float
    memory_peak: float
    cpu_percent: float
    thread_count: int
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def memory_used(self) -> float:
        """사용된 메모리 (MB)"""
        return self.memory_after - self.memory_before
    
    @property
    def memory_peak_increase(self) -> float:
        """피크 메모리 증가량 (MB)"""
        return self.memory_peak - self.memory_before


class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: List[PerformanceMetrics] = []
        self.active_monitors: Dict[str, Dict] = {}
        self.memory_tracker = deque(maxlen=1000)
        self.cpu_tracker = deque(maxlen=1000)
        
        # 백그라운드 모니터링
        self._monitoring = False
        self._monitor_thread = None
        
        # 프로세스 정보
        self.process = psutil.Process()
    
    def start_background_monitoring(self, interval: float = 1.0):
        """백그라운드 시스템 모니터링 시작"""
        if self._monitoring:
            return
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._background_monitor,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
    
    def stop_background_monitoring(self):
        """백그라운드 모니터링 중지"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
    
    def _background_monitor(self, interval: float):
        """백그라운드 모니터링 루프"""
        while self._monitoring:
            try:
                memory_mb = self.process.memory_info().rss / 1024 / 1024
                cpu_percent = self.process.cpu_percent()
                
                self.memory_tracker.append({
                    'timestamp': time.time(),
                    'memory': memory_mb
                })
                
                self.cpu_tracker.append({
                    'timestamp': time.time(),
                    'cpu': cpu_percent
                })
                
                time.sleep(interval)
            except Exception:
                break
    
    @contextmanager
    def monitor(self, name: str, **additional_data):
        """성능 모니터링 컨텍스트 매니저"""
        # 모니터링 시작
        start_info = self._get_system_info()
        start_time = time.time()
        
        try:
            yield
        finally:
            # 모니터링 종료
            end_time = time.time()
            end_info = self._get_system_info()
            
            # 메트릭스 생성
            metrics = PerformanceMetrics(
                name=name,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                memory_before=start_info['memory'],
                memory_after=end_info['memory'],
                memory_peak=max(start_info['memory'], end_info['memory']),
                cpu_percent=end_info['cpu'],
                thread_count=end_info['threads'],
                additional_data=additional_data
            )
            
            # 히스토리에 추가
            self.add_metrics(metrics)
    
    def _get_system_info(self) -> Dict[str, float]:
        """현재 시스템 정보 수집"""
        try:
            memory_mb = self.process.memory_info().rss / 1024 / 1024
            cpu_percent = self.process.cpu_percent()
            thread_count = self.process.num_threads()
            
            return {
                'memory': memory_mb,
                'cpu': cpu_percent,
                'threads': thread_count
            }
        except Exception:
            return {
                'memory': 0.0,
                'cpu': 0.0,
                'threads': 1
            }
    
    def add_metrics(self, metrics: PerformanceMetrics):
        """메트릭스 히스토리에 추가"""
        self.metrics_history.append(metrics)
        
        # 최대 개수 제한
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]
    
    def get_metrics_by_name(self, name: str) -> List[PerformanceMetrics]:
        """이름으로 메트릭스 필터링"""
        return [m for m in self.metrics_history if m.name == name]
    
    def get_summary_stats(self, name: Optional[str] = None) -> Dict[str, Any]:
        """요약 통계 생성"""
        if name:
            metrics = self.get_metrics_by_name(name)
        else:
            metrics = self.metrics_history
        
        if not metrics:
            return {}
        
        durations = [m.duration for m in metrics]
        memory_usage = [m.memory_used for m in metrics]
        cpu_usage = [m.cpu_percent for m in metrics]
        
        return {
            'count': len(metrics),
            'duration': {
                'mean': np.mean(durations),
                'std': np.std(durations),
                'min': np.min(durations),
                'max': np.max(durations),
                'total': np.sum(durations)
            },
            'memory': {
                'mean': np.mean(memory_usage),
                'std': np.std(memory_usage),
                'min': np.min(memory_usage),
                'max': np.max(memory_usage),
                'total': np.sum(memory_usage)
            },
            'cpu': {
                'mean': np.mean(cpu_usage),
                'std': np.std(cpu_usage),
                'min': np.min(cpu_usage),
                'max': np.max(cpu_usage)
            }
        }
    
    def generate_report(self, output_path: str = "performance_report.json"):
        """성능 리포트 생성"""
        # 전체 통계
        overall_stats = self.get_summary_stats()
        
        # 기능별 통계
        function_stats = {}
        unique_names = set(m.name for m in self.metrics_history)
        for name in unique_names:
            function_stats[name] = self.get_summary_stats(name)
        
        # 메모리 트렌드
        memory_trend = list(self.memory_tracker)
        cpu_trend = list(self.cpu_tracker)
        
        report = {
            'generated_at': time.time(),
            'overall_statistics': overall_stats,
            'function_statistics': function_stats,
            'memory_trend': memory_trend[-100:],  # 최근 100개
            'cpu_trend': cpu_trend[-100:],
            'recommendations': self._generate_recommendations()
        }
        
        # JSON으로 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """성능 개선 권장사항 생성"""
        recommendations = []
        
        if not self.metrics_history:
            return recommendations
        
        # 평균 메모리 사용량 체크
        avg_memory = np.mean([m.memory_used for m in self.metrics_history])
        if avg_memory > 500:  # 500MB 이상
            recommendations.append(
                f"높은 메모리 사용량 감지 (평균 {avg_memory:.1f}MB). "
                "배치 크기 줄이기나 중간 결과 삭제 고려"
            )
        
        # 실행 시간 체크
        avg_duration = np.mean([m.duration for m in self.metrics_history])
        if avg_duration > 10:  # 10초 이상
            recommendations.append(
                f"긴 실행 시간 감지 (평균 {avg_duration:.1f}초). "
                "병렬 처리나 알고리즘 최적화 고려"
            )
        
        # CPU 사용률 체크
        avg_cpu = np.mean([m.cpu_percent for m in self.metrics_history])
        if avg_cpu > 80:  # 80% 이상
            recommendations.append(
                f"높은 CPU 사용률 감지 (평균 {avg_cpu:.1f}%). "
                "작업 분산이나 스레드 수 조정 고려"
            )
        
        # 메모리 누수 체크
        if len(self.memory_tracker) > 10:
            recent_memory = [m['memory'] for m in list(self.memory_tracker)[-10:]]
            if len(set(recent_memory)) > 5:  # 메모리가 계속 변함
                memory_trend = np.polyfit(range(len(recent_memory)), recent_memory, 1)[0]
                if memory_trend > 1:  # 증가 추세
                    recommendations.append(
                        "메모리 사용량 증가 추세 감지. 메모리 누수 가능성 확인 필요"
                    )
        
        return recommendations
    
    def visualize_performance(self, output_dir: str = "performance_plots"):
        """성능 시각화"""
        Path(output_dir).mkdir(exist_ok=True)
        
        if not self.metrics_history:
            print("시각화할 성능 데이터가 없습니다.")
            return
        
        # 1. 실행 시간 히스토그램
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        durations = [m.duration for m in self.metrics_history]
        plt.hist(durations, bins=20, alpha=0.7, edgecolor='black')
        plt.xlabel('실행 시간 (초)')
        plt.ylabel('빈도')
        plt.title('실행 시간 분포')
        plt.grid(True, alpha=0.3)
        
        # 2. 메모리 사용량 히스토그램
        plt.subplot(2, 2, 2)
        memory_usage = [m.memory_used for m in self.metrics_history]
        plt.hist(memory_usage, bins=20, alpha=0.7, color='red', edgecolor='black')
        plt.xlabel('메모리 사용량 (MB)')
        plt.ylabel('빈도')
        plt.title('메모리 사용량 분포')
        plt.grid(True, alpha=0.3)
        
        # 3. 시간에 따른 메모리 트렌드
        plt.subplot(2, 2, 3)
        if self.memory_tracker:
            times = [m['timestamp'] for m in self.memory_tracker]
            memories = [m['memory'] for m in self.memory_tracker]
            times = [(t - times[0]) / 60 for t in times]  # 분 단위로 변환
            plt.plot(times, memories, 'b-', alpha=0.7)
            plt.xlabel('시간 (분)')
            plt.ylabel('메모리 (MB)')
            plt.title('메모리 사용량 트렌드')
            plt.grid(True, alpha=0.3)
        
        # 4. 기능별 성능 비교
        plt.subplot(2, 2, 4)
        unique_names = list(set(m.name for m in self.metrics_history))
        if len(unique_names) > 1:
            avg_durations = []
            for name in unique_names:
                name_metrics = self.get_metrics_by_name(name)
                avg_durations.append(np.mean([m.duration for m in name_metrics]))
            
            plt.bar(range(len(unique_names)), avg_durations, alpha=0.7)
            plt.xlabel('기능')
            plt.ylabel('평균 실행 시간 (초)')
            plt.title('기능별 성능 비교')
            plt.xticks(range(len(unique_names)), unique_names, rotation=45)
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/performance_overview.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"성능 시각화 결과가 {output_dir}/performance_overview.png에 저장되었습니다.")
    
    def clear_history(self):
        """히스토리 초기화"""
        self.metrics_history.clear()
        self.memory_tracker.clear()
        self.cpu_tracker.clear()


class FunctionProfiler:
    """함수별 프로파일링 데코레이터"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def __call__(self, func: Callable):
        """프로파일링 데코레이터"""
        def wrapper(*args, **kwargs):
            with self.monitor.monitor(func.__name__):
                return func(*args, **kwargs)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper


# 전역 모니터 인스턴스
global_monitor = PerformanceMonitor()

# 편의 함수들
def profile_function(func: Callable):
    """함수 프로파일링 데코레이터"""
    return FunctionProfiler(global_monitor)(func)

def monitor_performance(name: str, **kwargs):
    """성능 모니터링 컨텍스트 매니저"""
    return global_monitor.monitor(name, **kwargs)

def start_monitoring():
    """백그라운드 모니터링 시작"""
    global_monitor.start_background_monitoring()

def stop_monitoring():
    """백그라운드 모니터링 중지"""
    global_monitor.stop_background_monitoring()

def generate_performance_report(output_path: str = "performance_report.json"):
    """성능 리포트 생성"""
    return global_monitor.generate_report(output_path)

def visualize_performance(output_dir: str = "performance_plots"):
    """성능 시각화"""
    global_monitor.visualize_performance(output_dir)


if __name__ == '__main__':
    # 테스트 코드
    import argparse
    
    parser = argparse.ArgumentParser(description='성능 모니터링 도구 테스트')
    parser.add_argument('--test', action='store_true', help='테스트 실행')
    parser.add_argument('--report', action='store_true', help='리포트 생성')
    parser.add_argument('--visualize', action='store_true', help='시각화 생성')
    
    args = parser.parse_args()
    
    if args.test:
        print("성능 모니터링 테스트 시작...")
        
        # 테스트 함수들
        @profile_function
        def test_function_1():
            time.sleep(0.1)
            return np.random.random((1000, 1000))
        
        @profile_function
        def test_function_2():
            time.sleep(0.2)
            data = np.random.random((2000, 2000))
            return np.sum(data)
        
        # 백그라운드 모니터링 시작
        start_monitoring()
        
        # 테스트 실행
        for i in range(5):
            test_function_1()
            test_function_2()
        
        time.sleep(1)  # 백그라운드 모니터링 데이터 수집
        
        stop_monitoring()
        
        print("테스트 완료!")
    
    if args.report:
        report = generate_performance_report()
        print("성능 리포트가 생성되었습니다.")
        print(f"총 측정 횟수: {report['overall_statistics'].get('count', 0)}")
    
    if args.visualize:
        visualize_performance()
        print("성능 시각화가 생성되었습니다.")
