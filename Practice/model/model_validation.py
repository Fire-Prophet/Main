"""
모델 검증 및 분석 모듈
- 시뮬레이션 결과의 정확도 검증
- 실제 화재 데이터와의 비교 분석
- 통계적 검증 지표 계산
- 모델 성능 평가 및 시각화
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, roc_curve, auc, classification_report
from scipy import stats
from scipy.spatial.distance import cdist
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

class ModelValidator:
    """모델 검증 및 성능 평가 클래스"""
    
    def __init__(self, simulation_results: Dict, actual_data: Optional[Dict] = None):
        """
        Args:
            simulation_results: 시뮬레이션 결과 데이터
            actual_data: 실제 화재 데이터 (있는 경우)
        """
        self.simulation_results = simulation_results
        self.actual_data = actual_data
        self.validation_metrics = {}
        self.analysis_results = {}
        
    def validate_spread_pattern(self, actual_burned_area: np.ndarray = None) -> Dict:
        """화재 확산 패턴 검증"""
        print("화재 확산 패턴 검증 중...")
        
        final_state = self.simulation_results.get('final_grid', None)
        if final_state is None:
            raise ValueError("시뮬레이션 결과에 final_grid가 없습니다")
        
        # 연소된 영역 추출 (상태 2: 연소됨)
        burned_mask = (final_state == 2)
        
        pattern_metrics = {
            'total_burned_area': np.sum(burned_mask),
            'burn_ratio': np.sum(burned_mask) / burned_mask.size,
            'compactness': self._calculate_compactness(burned_mask),
            'circularity': self._calculate_circularity(burned_mask),
            'fractal_dimension': self._calculate_fractal_dimension(burned_mask)
        }
        
        # 실제 데이터와 비교 (있는 경우)
        if actual_burned_area is not None:
            comparison_metrics = self._compare_with_actual(burned_mask, actual_burned_area)
            pattern_metrics.update(comparison_metrics)
        
        self.validation_metrics['spread_pattern'] = pattern_metrics
        return pattern_metrics
    
    def validate_temporal_progression(self) -> Dict:
        """시간적 진행 패턴 검증"""
        print("시간적 진행 패턴 검증 중...")
        
        history = self.simulation_results.get('step_history', [])
        if not history:
            raise ValueError("시뮬레이션 결과에 step_history가 없습니다")
        
        burned_areas = []
        fire_perimeters = []
        
        for step_grid in history:
            burned_area = np.sum(step_grid == 2)
            burned_areas.append(burned_area)
            
            # 화재 경계선 길이 계산
            fire_mask = (step_grid == 1)
            perimeter = self._calculate_perimeter(fire_mask)
            fire_perimeters.append(perimeter)
        
        temporal_metrics = {
            'burn_rate_progression': self._analyze_burn_rate(burned_areas),
            'perimeter_growth': self._analyze_perimeter_growth(fire_perimeters),
            'acceleration_phases': self._detect_acceleration_phases(burned_areas),
            'growth_consistency': self._calculate_growth_consistency(burned_areas)
        }
        
        self.validation_metrics['temporal_progression'] = temporal_metrics
        return temporal_metrics
    
    def validate_fuel_response(self) -> Dict:
        """연료 타입별 반응 검증"""
        print("연료 타입별 반응 검증 중...")
        
        fuel_map = self.simulation_results.get('fuel_map', None)
        final_state = self.simulation_results.get('final_grid', None)
        
        if fuel_map is None or final_state is None:
            raise ValueError("연료 맵 또는 최종 상태 데이터가 없습니다")
        
        fuel_response = {}
        unique_fuels = np.unique(fuel_map)
        
        for fuel_type in unique_fuels:
            fuel_mask = (fuel_map == fuel_type)
            fuel_burned = np.logical_and(fuel_mask, final_state == 2)
            
            total_fuel_cells = np.sum(fuel_mask)
            burned_fuel_cells = np.sum(fuel_burned)
            
            if total_fuel_cells > 0:
                burn_ratio = burned_fuel_cells / total_fuel_cells
                fuel_response[str(fuel_type)] = {
                    'total_cells': int(total_fuel_cells),
                    'burned_cells': int(burned_fuel_cells),
                    'burn_ratio': float(burn_ratio)
                }
        
        # 연료별 평균 연소율 분석
        fuel_burn_rates = [data['burn_ratio'] for data in fuel_response.values()]
        fuel_stats = {
            'mean_burn_rate': np.mean(fuel_burn_rates),
            'std_burn_rate': np.std(fuel_burn_rates),
            'max_burn_rate': np.max(fuel_burn_rates),
            'min_burn_rate': np.min(fuel_burn_rates)
        }
        
        fuel_response['statistics'] = fuel_stats
        self.validation_metrics['fuel_response'] = fuel_response
        return fuel_response
    
    def calculate_confusion_matrix(self, actual_burned_area: np.ndarray) -> Dict:
        """혼동 행렬 계산"""
        print("혼동 행렬 계산 중...")
        
        final_state = self.simulation_results.get('final_grid', None)
        if final_state is None:
            raise ValueError("시뮬레이션 결과에 final_grid가 없습니다")
        
        # 예측값과 실제값을 이진 분류로 변환
        predicted = (final_state == 2).astype(int).flatten()
        actual = actual_burned_area.astype(int).flatten()
        
        # 크기 맞추기
        min_size = min(len(predicted), len(actual))
        predicted = predicted[:min_size]
        actual = actual[:min_size]
        
        # 분류 성능 지표 계산
        accuracy = accuracy_score(actual, predicted)
        precision = precision_score(actual, predicted, zero_division=0)
        recall = recall_score(actual, predicted, zero_division=0)
        f1 = f1_score(actual, predicted, zero_division=0)
        
        cm = confusion_matrix(actual, predicted)
        
        confusion_metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'confusion_matrix': cm.tolist(),
            'classification_report': classification_report(actual, predicted, output_dict=True)
        }
        
        self.validation_metrics['confusion_matrix'] = confusion_metrics
        return confusion_metrics
    
    def calculate_roc_metrics(self, actual_burned_area: np.ndarray) -> Dict:
        """ROC 곡선 및 AUC 계산"""
        print("ROC 곡선 및 AUC 계산 중...")
        
        final_state = self.simulation_results.get('final_grid', None)
        if final_state is None:
            raise ValueError("시뮬레이션 결과에 final_grid가 없습니다")
        
        # 확률 점수로 변환 (연소 상태를 확률로 해석)
        prob_scores = final_state.flatten() / 2.0  # 0, 0.5, 1.0으로 정규화
        actual = actual_burned_area.astype(int).flatten()
        
        # 크기 맞추기
        min_size = min(len(prob_scores), len(actual))
        prob_scores = prob_scores[:min_size]
        actual = actual[:min_size]
        
        try:
            fpr, tpr, thresholds = roc_curve(actual, prob_scores)
            roc_auc = auc(fpr, tpr)
            
            roc_metrics = {
                'fpr': fpr.tolist(),
                'tpr': tpr.tolist(),
                'thresholds': thresholds.tolist(),
                'auc': float(roc_auc)
            }
        except Exception as e:
            print(f"ROC 계산 중 오류: {e}")
            roc_metrics = {
                'fpr': [],
                'tpr': [],
                'thresholds': [],
                'auc': 0.0
            }
        
        self.validation_metrics['roc_metrics'] = roc_metrics
        return roc_metrics
    
    def _calculate_compactness(self, burned_mask: np.ndarray) -> float:
        """연소 영역의 컴팩트성 계산"""
        if np.sum(burned_mask) == 0:
            return 0.0
        
        area = np.sum(burned_mask)
        perimeter = self._calculate_perimeter(burned_mask)
        
        if perimeter == 0:
            return 0.0
        
        compactness = (4 * np.pi * area) / (perimeter ** 2)
        return float(compactness)
    
    def _calculate_circularity(self, burned_mask: np.ndarray) -> float:
        """연소 영역의 원형성 계산"""
        coords = np.where(burned_mask)
        if len(coords[0]) == 0:
            return 0.0
        
        # 무게중심 계산
        center_y, center_x = np.mean(coords[0]), np.mean(coords[1])
        
        # 중심에서 각 점까지의 거리
        distances = np.sqrt((coords[0] - center_y)**2 + (coords[1] - center_x)**2)
        
        if len(distances) == 0:
            return 0.0
        
        mean_radius = np.mean(distances)
        std_radius = np.std(distances)
        
        if mean_radius == 0:
            return 0.0
        
        circularity = 1 - (std_radius / mean_radius)
        return float(max(0, circularity))
    
    def _calculate_fractal_dimension(self, burned_mask: np.ndarray) -> float:
        """프랙탈 차원 계산 (박스 카운팅 방법)"""
        def box_count(image, box_size):
            h, w = image.shape
            count = 0
            for i in range(0, h, box_size):
                for j in range(0, w, box_size):
                    box = image[i:i+box_size, j:j+box_size]
                    if np.any(box):
                        count += 1
            return count
        
        sizes = [1, 2, 4, 8, 16]
        counts = []
        
        for size in sizes:
            if size < min(burned_mask.shape):
                count = box_count(burned_mask, size)
                counts.append(count)
            else:
                break
        
        if len(counts) < 2:
            return 0.0
        
        # 로그-로그 플롯의 기울기로 프랙탈 차원 계산
        log_sizes = np.log(sizes[:len(counts)])
        log_counts = np.log(counts)
        
        if len(log_sizes) > 1:
            slope, _ = np.polyfit(log_sizes, log_counts, 1)
            fractal_dim = -slope
            return float(fractal_dim)
        
        return 0.0
    
    def _calculate_perimeter(self, mask: np.ndarray) -> int:
        """마스크의 둘레 계산"""
        # 경계선 검출 (간단한 방법)
        padded = np.pad(mask.astype(int), 1, mode='constant', constant_values=0)
        kernel = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]])
        
        from scipy.ndimage import convolve
        edges = convolve(padded, kernel, mode='constant')
        perimeter = np.sum(edges > 0)
        
        return int(perimeter)
    
    def _compare_with_actual(self, predicted_mask: np.ndarray, actual_mask: np.ndarray) -> Dict:
        """실제 데이터와의 비교 분석"""
        # 크기 맞추기
        min_h = min(predicted_mask.shape[0], actual_mask.shape[0])
        min_w = min(predicted_mask.shape[1], actual_mask.shape[1])
        
        pred_resized = predicted_mask[:min_h, :min_w]
        actual_resized = actual_mask[:min_h, :min_w]
        
        # 면적 비교
        pred_area = np.sum(pred_resized)
        actual_area = np.sum(actual_resized)
        
        # 교집합과 합집합
        intersection = np.sum(np.logical_and(pred_resized, actual_resized))
        union = np.sum(np.logical_or(pred_resized, actual_resized))
        
        # Jaccard 유사도 (IoU)
        jaccard = intersection / union if union > 0 else 0
        
        # 면적 오차
        area_error = abs(pred_area - actual_area) / actual_area if actual_area > 0 else float('inf')
        
        return {
            'jaccard_similarity': float(jaccard),
            'area_error_ratio': float(area_error),
            'predicted_area': int(pred_area),
            'actual_area': int(actual_area),
            'intersection_area': int(intersection),
            'union_area': int(union)
        }
    
    def _analyze_burn_rate(self, burned_areas: List[int]) -> Dict:
        """연소율 진행 분석"""
        if len(burned_areas) < 2:
            return {'rates': [], 'mean_rate': 0, 'acceleration': 0}
        
        rates = np.diff(burned_areas)
        
        return {
            'rates': rates.tolist(),
            'mean_rate': float(np.mean(rates)),
            'max_rate': float(np.max(rates)),
            'min_rate': float(np.min(rates)),
            'rate_variance': float(np.var(rates)),
            'acceleration': float(np.mean(np.diff(rates))) if len(rates) > 1 else 0
        }
    
    def _analyze_perimeter_growth(self, perimeters: List[int]) -> Dict:
        """둘레 성장 분석"""
        if len(perimeters) < 2:
            return {'growth_rates': [], 'mean_growth': 0}
        
        growth_rates = np.diff(perimeters)
        
        return {
            'growth_rates': growth_rates.tolist(),
            'mean_growth': float(np.mean(growth_rates)),
            'max_growth': float(np.max(growth_rates)),
            'min_growth': float(np.min(growth_rates))
        }
    
    def _detect_acceleration_phases(self, burned_areas: List[int]) -> Dict:
        """가속 구간 감지"""
        if len(burned_areas) < 3:
            return {'phases': [], 'acceleration_periods': 0}
        
        rates = np.diff(burned_areas)
        accelerations = np.diff(rates)
        
        # 가속 구간 (가속도가 양수인 구간)
        acceleration_phases = []
        in_acceleration = False
        start_idx = 0
        
        for i, acc in enumerate(accelerations):
            if acc > 0 and not in_acceleration:
                in_acceleration = True
                start_idx = i
            elif acc <= 0 and in_acceleration:
                in_acceleration = False
                acceleration_phases.append((start_idx, i))
        
        if in_acceleration:
            acceleration_phases.append((start_idx, len(accelerations)))
        
        return {
            'phases': acceleration_phases,
            'acceleration_periods': len(acceleration_phases),
            'total_acceleration_steps': sum(end - start for start, end in acceleration_phases)
        }
    
    def _calculate_growth_consistency(self, burned_areas: List[int]) -> float:
        """성장 일관성 계산"""
        if len(burned_areas) < 2:
            return 0.0
        
        rates = np.diff(burned_areas)
        if len(rates) == 0:
            return 0.0
        
        # 변동계수 (coefficient of variation)
        mean_rate = np.mean(rates)
        if mean_rate == 0:
            return 0.0
        
        cv = np.std(rates) / mean_rate
        consistency = 1 / (1 + cv)  # 일관성 점수 (0~1)
        
        return float(consistency)
    
    def generate_validation_report(self, output_dir: str = "validation_results") -> str:
        """검증 보고서 생성"""
        print("검증 보고서 생성 중...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # JSON 보고서
        report_data = {
            'validation_timestamp': datetime.now().isoformat(),
            'metrics': self.validation_metrics,
            'summary': self._generate_summary()
        }
        
        report_path = os.path.join(output_dir, 'validation_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # 시각화 생성
        self._create_validation_plots(output_dir)
        
        print(f"검증 보고서가 {output_dir}에 저장되었습니다.")
        return report_path
    
    def _generate_summary(self) -> Dict:
        """검증 결과 요약"""
        summary = {
            'total_metrics': len(self.validation_metrics),
            'validation_score': 0.0,
            'recommendations': []
        }
        
        # 간단한 종합 점수 계산
        scores = []
        
        if 'confusion_matrix' in self.validation_metrics:
            scores.append(self.validation_metrics['confusion_matrix']['f1_score'])
        
        if 'spread_pattern' in self.validation_metrics:
            compactness = self.validation_metrics['spread_pattern'].get('compactness', 0)
            scores.append(min(compactness, 1.0))
        
        if 'temporal_progression' in self.validation_metrics:
            consistency = self.validation_metrics['temporal_progression'].get('growth_consistency', 0)
            scores.append(consistency)
        
        if scores:
            summary['validation_score'] = float(np.mean(scores))
        
        # 추천사항 생성
        if summary['validation_score'] < 0.5:
            summary['recommendations'].append("모델 파라미터 조정 필요")
            summary['recommendations'].append("연료 타입별 확산 확률 재검토")
        
        if 'fuel_response' in self.validation_metrics:
            fuel_stats = self.validation_metrics['fuel_response'].get('statistics', {})
            if fuel_stats.get('std_burn_rate', 0) > 0.3:
                summary['recommendations'].append("연료별 연소 특성 차별화 개선")
        
        return summary
    
    def _create_validation_plots(self, output_dir: str):
        """검증 시각화 생성"""
        try:
            # 1. 혼동 행렬 플롯
            if 'confusion_matrix' in self.validation_metrics:
                self._plot_confusion_matrix(output_dir)
            
            # 2. ROC 곡선
            if 'roc_metrics' in self.validation_metrics:
                self._plot_roc_curve(output_dir)
            
            # 3. 시간적 진행 플롯
            if 'temporal_progression' in self.validation_metrics:
                self._plot_temporal_progression(output_dir)
            
            # 4. 연료별 반응 플롯
            if 'fuel_response' in self.validation_metrics:
                self._plot_fuel_response(output_dir)
                
        except Exception as e:
            print(f"시각화 생성 중 오류: {e}")
    
    def _plot_confusion_matrix(self, output_dir: str):
        """혼동 행렬 시각화"""
        cm_data = self.validation_metrics['confusion_matrix']
        cm = np.array(cm_data['confusion_matrix'])
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Not Burned', 'Burned'],
                   yticklabels=['Not Burned', 'Burned'])
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        
        # 성능 지표 텍스트 추가
        metrics_text = f"Accuracy: {cm_data['accuracy']:.3f}\n"
        metrics_text += f"Precision: {cm_data['precision']:.3f}\n"
        metrics_text += f"Recall: {cm_data['recall']:.3f}\n"
        metrics_text += f"F1-Score: {cm_data['f1_score']:.3f}"
        
        plt.text(1.1, 0.5, metrics_text, transform=plt.gca().transAxes,
                verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat'))
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_roc_curve(self, output_dir: str):
        """ROC 곡선 시각화"""
        roc_data = self.validation_metrics['roc_metrics']
        
        if not roc_data['fpr'] or not roc_data['tpr']:
            return
        
        plt.figure(figsize=(8, 6))
        plt.plot(roc_data['fpr'], roc_data['tpr'], 
                label=f'ROC Curve (AUC = {roc_data["auc"]:.3f})')
        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
        
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'roc_curve.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_temporal_progression(self, output_dir: str):
        """시간적 진행 시각화"""
        temporal_data = self.validation_metrics['temporal_progression']
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 연소율 변화
        rates = temporal_data['burn_rate_progression']['rates']
        if rates:
            axes[0, 0].plot(rates)
            axes[0, 0].set_title('Burn Rate Progression')
            axes[0, 0].set_xlabel('Time Step')
            axes[0, 0].set_ylabel('Burn Rate (cells/step)')
            axes[0, 0].grid(True, alpha=0.3)
        
        # 둘레 성장
        growth_rates = temporal_data['perimeter_growth']['growth_rates']
        if growth_rates:
            axes[0, 1].plot(growth_rates)
            axes[0, 1].set_title('Perimeter Growth')
            axes[0, 1].set_xlabel('Time Step')
            axes[0, 1].set_ylabel('Perimeter Growth')
            axes[0, 1].grid(True, alpha=0.3)
        
        # 가속 구간
        phases = temporal_data['acceleration_phases']['phases']
        if rates and phases:
            axes[1, 0].plot(rates)
            for start, end in phases:
                axes[1, 0].axvspan(start, end, alpha=0.3, color='red')
            axes[1, 0].set_title('Acceleration Phases')
            axes[1, 0].set_xlabel('Time Step')
            axes[1, 0].set_ylabel('Burn Rate')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 통계 요약
        stats_text = f"Mean Burn Rate: {temporal_data['burn_rate_progression']['mean_rate']:.2f}\n"
        stats_text += f"Growth Consistency: {temporal_data['growth_consistency']:.3f}\n"
        stats_text += f"Acceleration Periods: {temporal_data['acceleration_phases']['acceleration_periods']}"
        
        axes[1, 1].text(0.1, 0.5, stats_text, transform=axes[1, 1].transAxes,
                       verticalalignment='center', fontsize=12,
                       bbox=dict(boxstyle='round', facecolor='lightblue'))
        axes[1, 1].set_title('Statistics Summary')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'temporal_progression.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_fuel_response(self, output_dir: str):
        """연료별 반응 시각화"""
        fuel_data = self.validation_metrics['fuel_response']
        
        # 통계 데이터 제외
        fuel_types = []
        burn_ratios = []
        
        for fuel_type, data in fuel_data.items():
            if fuel_type != 'statistics' and isinstance(data, dict):
                fuel_types.append(fuel_type)
                burn_ratios.append(data['burn_ratio'])
        
        if not fuel_types:
            return
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(fuel_types, burn_ratios)
        
        # 색상 그라디언트
        colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(burn_ratios)))
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        plt.title('Burn Ratio by Fuel Type')
        plt.xlabel('Fuel Type')
        plt.ylabel('Burn Ratio')
        plt.xticks(rotation=45)
        
        # 평균선 추가
        mean_ratio = np.mean(burn_ratios)
        plt.axhline(y=mean_ratio, color='red', linestyle='--', 
                   label=f'Mean: {mean_ratio:.3f}')
        plt.legend()
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'fuel_response.png'), dpi=300, bbox_inches='tight')
        plt.close()


# 유틸리티 함수들
def load_simulation_results(result_dir: str) -> Dict:
    """시뮬레이션 결과 로드"""
    results = {}
    
    # 단계별 결과 로드
    step_files = sorted([f for f in os.listdir(result_dir) if f.startswith('step_') and f.endswith('.npy')])
    if step_files:
        step_history = []
        for step_file in step_files:
            step_data = np.load(os.path.join(result_dir, step_file))
            step_history.append(step_data)
        results['step_history'] = step_history
        results['final_grid'] = step_history[-1] if step_history else None
    
    # 연료 맵 로드 (있는 경우)
    fuel_map_path = os.path.join(result_dir, 'fuel_map.npy')
    if os.path.exists(fuel_map_path):
        results['fuel_map'] = np.load(fuel_map_path)
    
    return results

def create_synthetic_actual_data(final_grid: np.ndarray, noise_level: float = 0.1) -> np.ndarray:
    """테스트용 가상 실제 데이터 생성"""
    actual_data = final_grid.copy()
    
    # 노이즈 추가
    noise = np.random.random(actual_data.shape) < noise_level
    actual_data[noise] = 1 - actual_data[noise]  # 일부 값 뒤집기
    
    return actual_data

if __name__ == "__main__":
    # 사용 예시
    print("모델 검증 분석 모듈 테스트")
    
    # 테스트용 데이터 생성
    test_grid = np.random.choice([0, 1, 2], size=(50, 50), p=[0.6, 0.2, 0.2])
    test_fuel_map = np.random.choice(['TL1', 'TU1', 'GS1'], size=(50, 50))
    
    test_results = {
        'final_grid': test_grid,
        'fuel_map': test_fuel_map,
        'step_history': [test_grid] * 10  # 간단한 히스토리
    }
    
    # 검증기 생성 및 테스트
    validator = ModelValidator(test_results)
    
    # 각종 검증 수행
    pattern_metrics = validator.validate_spread_pattern()
    print("확산 패턴 검증 완료")
    
    temporal_metrics = validator.validate_temporal_progression()
    print("시간적 진행 검증 완료")
    
    fuel_metrics = validator.validate_fuel_response()
    print("연료별 반응 검증 완료")
    
    # 보고서 생성
    report_path = validator.generate_validation_report("test_validation")
    print(f"검증 보고서 생성: {report_path}")
