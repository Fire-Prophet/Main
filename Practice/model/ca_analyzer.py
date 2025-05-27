import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import json

class CAAnalyzer:
    """CA 시뮬레이션 결과 분석 도구"""
    
    def __init__(self, result_dir):
        self.result_dir = Path(result_dir)
        self.stats = []
        
    def analyze_step(self, step_file):
        """단일 스텝 분석"""
        grid = np.load(step_file)
        step_num = int(step_file.stem.split('_')[1])
        
        total_cells = grid.size
        empty_cells = np.sum(grid == 0)
        tree_cells = np.sum(grid == 1) 
        burning_cells = np.sum(grid == 2)
        
        burned_area = total_cells - tree_cells - empty_cells  # 이미 탄 영역
        fire_perimeter = self._calculate_perimeter(grid == 2)
        
        return {
            'step': step_num,
            'total_cells': total_cells,
            'empty_cells': empty_cells,
            'tree_cells': tree_cells,
            'burning_cells': burning_cells,
            'burned_area': burned_area,
            'fire_perimeter': fire_perimeter,
            'burn_ratio': (total_cells - tree_cells) / total_cells
        }
    
    def _calculate_perimeter(self, burning_mask):
        """화재 경계선 길이 계산"""
        # 간단한 경계선 계산 (4-connectivity)
        from scipy import ndimage
        eroded = ndimage.binary_erosion(burning_mask)
        perimeter = burning_mask.astype(int) - eroded.astype(int)
        return np.sum(perimeter)
    
    def analyze_all_steps(self):
        """모든 스텝 분석"""
        step_files = sorted(self.result_dir.glob('step_*.npy'))
        
        for step_file in step_files:
            stat = self.analyze_step(step_file)
            self.stats.append(stat)
            
        self.df = pd.DataFrame(self.stats)
        return self.df
    
    def plot_fire_progression(self, save_path=None):
        """화재 확산 진행 그래프"""
        if not hasattr(self, 'df'):
            self.analyze_all_steps()
            
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 연소 면적 변화
        axes[0,0].plot(self.df['step'], self.df['burned_area'], 'r-', linewidth=2)
        axes[0,0].set_title('연소 면적 변화')
        axes[0,0].set_xlabel('시간 (스텝)')
        axes[0,0].set_ylabel('연소된 셀 수')
        axes[0,0].grid(True)
        
        # 활성 화재 면적
        axes[0,1].plot(self.df['step'], self.df['burning_cells'], 'orange', linewidth=2)
        axes[0,1].set_title('활성 화재 면적')
        axes[0,1].set_xlabel('시간 (스텝)')
        axes[0,1].set_ylabel('연소중인 셀 수')
        axes[0,1].grid(True)
        
        # 화재 경계선 길이
        axes[1,0].plot(self.df['step'], self.df['fire_perimeter'], 'g-', linewidth=2)
        axes[1,0].set_title('화재 경계선 길이')
        axes[1,0].set_xlabel('시간 (스텝)')
        axes[1,0].set_ylabel('경계선 길이')
        axes[1,0].grid(True)
        
        # 연소율 (%)
        axes[1,1].plot(self.df['step'], self.df['burn_ratio']*100, 'purple', linewidth=2)
        axes[1,1].set_title('전체 연소율')
        axes[1,1].set_xlabel('시간 (스텝)')
        axes[1,1].set_ylabel('연소율 (%)')
        axes[1,1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def calculate_spread_rate(self):
        """화재 확산 속도 계산"""
        if not hasattr(self, 'df'):
            self.analyze_all_steps()
            
        # 연소 면적 증가율
        burned_diff = self.df['burned_area'].diff().fillna(0)
        self.df['spread_rate'] = burned_diff
        
        return self.df[['step', 'spread_rate']]
    
    def save_analysis_report(self, report_path=None):
        """분석 결과 저장"""
        if not hasattr(self, 'df'):
            self.analyze_all_steps()
            
        report_path = report_path or self.result_dir / 'analysis_report.json'
        
        summary = {
            'total_steps': len(self.df),
            'max_burned_area': float(self.df['burned_area'].max()),
            'final_burn_ratio': float(self.df['burn_ratio'].iloc[-1]),
            'peak_fire_intensity': float(self.df['burning_cells'].max()),
            'average_spread_rate': float(self.df['burned_area'].diff().mean()),
            'simulation_stats': self.df.to_dict('records')
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        print(f"분석 보고서 저장: {report_path}")
        return summary

if __name__ == '__main__':
    # 사용 예시
    analyzer = CAAnalyzer('ca_results')
    
    # 전체 분석
    df = analyzer.analyze_all_steps()
    print("분석 완료!")
    print(f"총 {len(df)} 스텝 분석됨")
    
    # 시각화
    analyzer.plot_fire_progression('ca_results/fire_progression.png')
    
    # 확산 속도 계산
    spread_df = analyzer.calculate_spread_rate()
    print("\n확산 속도:")
    print(spread_df.head(10))
    
    # 보고서 저장
    summary = analyzer.save_analysis_report()
    print(f"\n최종 연소율: {summary['final_burn_ratio']:.2%}")
