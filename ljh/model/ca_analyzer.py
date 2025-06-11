import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import json
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import seaborn as sns

class CAAnalyzer:
    """CA 시뮬레이션 결과 분석 도구"""
    
    def __init__(self, result_dir):
        self.result_dir = Path(result_dir)
        self.stats = []
        
        # Anderson13 연료타입별 색상 정의
        self.fuel_colors = {
            'TL1': '#228B22',  # 침엽수림 - 진한 녹색
            'TL2': '#32CD32',  # 활엽수림 - 라임 그린
            'TL3': '#90EE90',  # 혼효림 - 연한 녹색
            'TU1': '#006400',  # 침엽수림 밀집 - 다크 그린
            'TU2': '#2E8B57',  # 침엽수림 중밀도 - 씨 그린
            'TU3': '#8FBC8F',  # 활엽수림 밀집 - 다크씨그린
            'TU4': '#9ACD32',  # 활엽수림 중밀도 - 옐로우그린
            'TU5': '#556B2F',  # 혼효림 밀집 - 다크올리브그린
            'GS1': '#F4A460',  # 죽림 - 샌디브라운
            'GR1': '#ADFF2F',  # 초지 - 그린옐로우
            'SH1': '#8B4513',  # 관목덤불 - 새들브라운
            'NB1': '#D2B48C'   # 비산림 - 탄색
        }
        
        # CA 상태별 색상 (0: 빈공간, 1: 나무, 2: 화재, 3: 연소후)
        self.state_colors = ['#FFFFFF', '#228B22', '#FF4500', '#2F4F4F']
        self.state_cmap = ListedColormap(self.state_colors)
        
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
    
    def create_animation(self, output_path=None, fps=5, dpi=100):
        """화재 확산 애니메이션 생성"""
        step_files = sorted(self.result_dir.glob('step_*.npy'))
        if not step_files:
            print("애니메이션 생성을 위한 스텝 파일이 없습니다.")
            return
            
        output_path = output_path or self.result_dir / 'fire_animation.mp4'
        
        # 첫 번째 프레임으로 figure 설정
        first_grid = np.load(step_files[0])
        fig, ax = plt.subplots(figsize=(10, 10))
        
        im = ax.imshow(first_grid, cmap=self.state_cmap, vmin=0, vmax=3, 
                        interpolation='nearest', animated=True)
        ax.set_title('화재 확산 시뮬레이션', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        # 컬러바 추가
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_ticks([0, 1, 2, 3])
        cbar.set_ticklabels(['빈공간', '나무', '화재', '연소후'])
        
        def animate(frame):
            if frame < len(step_files):
                grid = np.load(step_files[frame])
                im.set_array(grid)
                ax.set_title(f'화재 확산 시뮬레이션 - Step {frame}', 
                              fontsize=16, fontweight='bold')
            return [im]
        
        anim = animation.FuncAnimation(fig, animate, frames=len(step_files),
                                   interval=1000//fps, blit=True, repeat=True)
        
        # 저장
        anim.save(output_path, writer='ffmpeg', fps=fps, dpi=dpi,
                  savefig_kwargs={'bbox_inches': 'tight'})
        plt.close()
        
        print(f"애니메이션 저장 완료: {output_path}")
        return anim
    
    def plot_fuel_distribution(self, fuel_map, save_path=None):
        """연료타입별 분포 시각화"""
        if fuel_map is None:
            print("연료맵이 제공되지 않았습니다.")
            return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 연료타입 분포 맵
        unique_fuels = np.unique(fuel_map)
        colors = [self.fuel_colors.get(fuel, '#808080') for fuel in unique_fuels]
        fuel_cmap = ListedColormap(colors)
        
        # 숫자 인덱스로 변환하여 시각화
        fuel_indices = np.zeros_like(fuel_map, dtype=int)
        for i, fuel in enumerate(unique_fuels):
            fuel_indices[fuel_map == fuel] = i
        
        im1 = ax1.imshow(fuel_indices, cmap=fuel_cmap, vmin=0, vmax=len(unique_fuels)-1)
        ax1.set_title('연료타입 분포', fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        # 컬러바
        cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
        cbar1.set_ticks(range(len(unique_fuels)))
        cbar1.set_ticklabels(unique_fuels)
        
        # 연료타입별 면적 비율 차트
        fuel_counts = pd.Series(fuel_map.flatten()).value_counts()
        fuel_percentages = (fuel_counts / fuel_counts.sum() * 100).sort_index()
        
        bars = ax2.bar(range(len(fuel_percentages)), fuel_percentages.values,
                     color=[self.fuel_colors.get(fuel, '#808080') 
                            for fuel in fuel_percentages.index])
        ax2.set_title('연료타입별 면적 비율', fontsize=14, fontweight='bold')
        ax2.set_xlabel('연료타입')
        ax2.set_ylabel('면적 비율 (%)')
        ax2.set_xticks(range(len(fuel_percentages)))
        ax2.set_xticklabels(fuel_percentages.index, rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # 각 막대 위에 퍼센트 표시
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_advanced_analysis(self, save_path=None):
        """고급 분석 시각화 (히트맵, 상관관계 등)"""
        if not hasattr(self, 'df'):
            self.analyze_all_steps()
            
        fig = plt.figure(figsize=(16, 12))
        
        # 1. 화재 확산 속도 히트맵
        ax1 = plt.subplot(3, 3, 1)
        spread_rates = self.df['burned_area'].diff().fillna(0)
        time_heatmap = spread_rates.values.reshape(-1, 1)
        sns.heatmap(time_heatmap.T, cmap='Reds', ax=ax1, cbar_kws={'label': '확산속도'})
        ax1.set_title('시간별 화재 확산속도')
        ax1.set_xlabel('시간 (스텝)')
        
        # 2. 누적 연소면적
        ax2 = plt.subplot(3, 3, 2)
        ax2.fill_between(self.df['step'], self.df['burned_area'], alpha=0.7, color='red')
        ax2.plot(self.df['step'], self.df['burned_area'], 'r-', linewidth=2)
        ax2.set_title('누적 연소면적')
        ax2.set_xlabel('시간 (스텝)')
        ax2.set_ylabel('연소된 셀 수')
        ax2.grid(True, alpha=0.3)
        
        # 3. 화재 강도 (활성 화재 면적)
        ax3 = plt.subplot(3, 3, 3)
        ax3.plot(self.df['step'], self.df['burning_cells'], 'orange', linewidth=2, marker='o', markersize=3)
        ax3.set_title('화재 강도 (활성 화재)')
        ax3.set_xlabel('시간 (스텝)')
        ax3.set_ylabel('연소중인 셀 수')
        ax3.grid(True, alpha=0.3)
    
        # 4. 화재 경계선 길이 변화
        ax4 = plt.subplot(3, 3, 4)
        ax4.plot(self.df['step'], self.df['fire_perimeter'], 'g-', linewidth=2)
        ax4.set_title('화재 경계선 길이')
        ax4.set_xlabel('시간 (스텝)')
        ax4.set_ylabel('경계선 길이')
        ax4.grid(True, alpha=0.3)
        
        # 5. 연소율 곡선
        ax5 = plt.subplot(3, 3, 5)
        ax5.plot(self.df['step'], self.df['burn_ratio']*100, 'purple', linewidth=2)
        ax5.set_title('연소율 변화')
        ax5.set_xlabel('시간 (스텝)')
        ax5.set_ylabel('연소율 (%)')
        ax5.grid(True, alpha=0.3)
        
        # 6. 로그 스케일 확산
        ax6 = plt.subplot(3, 3, 6)
        ax6.semilogy(self.df['step'], self.df['burned_area'] + 1)
        ax6.set_title('로그 스케일 연소면적')
        ax6.set_xlabel('시간 (스텝)')
        ax6.set_ylabel('연소면적 (log)')
        ax6.grid(True, alpha=0.3)
        
        # 7. 상관관계 히트맵
        ax7 = plt.subplot(3, 3, 7)
        corr_data = self.df[['burned_area', 'burning_cells', 'fire_perimeter', 'burn_ratio']].corr()
        sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0, ax=ax7)
        ax7.set_title('변수간 상관관계')
        
        # 8. 분포 히스토그램
        ax8 = plt.subplot(3, 3, 8)
        spread_rate = self.df['burned_area'].diff().fillna(0)
        ax8.hist(spread_rate, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax8.set_title('확산속도 분포')
        ax8.set_xlabel('확산속도 (셀/스텝)')
        ax8.set_ylabel('빈도')
        ax8.grid(True, alpha=0.3)
        
        # 9. 요약 통계
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        stats_text = f"""
        시뮬레이션 요약 통계
        
        총 스텝 수: {len(self.df)}
        최대 연소면적: {self.df['burned_area'].max():,}
        최종 연소율: {self.df['burn_ratio'].iloc[-1]:.2%}
        최대 화재강도: {self.df['burning_cells'].max():,}
        평균 확산속도: {spread_rate.mean():.2f}
        최대 확산속도: {spread_rate.max():.2f}
        """
        ax9.text(0.1, 0.9, stats_text, transform=ax9.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def export_analysis_data(self, output_path=None):
        """분석 데이터를 CSV, Excel로 내보내기"""
        if not hasattr(self, 'df'):
            self.analyze_all_steps()
            
        output_path = output_path or self.result_dir / 'analysis_data'
        
        # CSV 저장
        csv_path = f"{output_path}.csv"
        self.df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # Excel 저장 (여러 시트)
        excel_path = f"{output_path}.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # 기본 분석 데이터
            self.df.to_excel(writer, sheet_name='시뮬레이션데이터', index=False)
            
            # 요약 통계
            summary_stats = self.df.describe()
            summary_stats.to_excel(writer, sheet_name='요약통계')
            
            # 확산속도 분석
            spread_rate = self.df['burned_area'].diff().fillna(0)
            spread_analysis = pd.DataFrame({
                'step': self.df['step'],
                'spread_rate': spread_rate,
                'cumulative_burned': self.df['burned_area'],
                'active_fire': self.df['burning_cells']
            })
            spread_analysis.to_excel(writer, sheet_name='확산속도분석', index=False)
        
        print(f"분석 데이터 저장 완료:")
        print(f"  CSV: {csv_path}")
        print(f"  Excel: {excel_path}")
    
# This is another comment for a new commit.
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
