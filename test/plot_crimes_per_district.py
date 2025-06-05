# filename: plot_crimes_per_district.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정 (Windows: Malgun Gothic, macOS: AppleGothic)
# 시스템에 맞는 폰트 이름을 사용해야 합니다.
try:
    import platform
    if platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    elif platform.system() == 'Darwin': # macOS
        plt.rc('font', family='AppleGothic')
    else: # Linux
        # 예: NanumGothic (설치 필요)
        plt.rc('font', family='NanumGothic')
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지
except Exception as e:
    print(f"폰트 설정 중 오류: {e}. 기본 폰트로 진행합니다.")


def plot_total_crimes_by_district(df, year=None):
    """
    구별 총 범죄 건수를 막대 그래프로 시각화합니다.
    특정 연도(year)가 주어지면 해당 연도의 데이터만 사용합니다.
    """
    if df is None or 'District' not in df.columns or 'Cases' not in df.columns:
        print("오류: 'District' 또는 'Cases' 컬럼이 데이터에 없습니다.")
        return

    target_df = df.copy()
    plot_title = "인천시 구별 총 범죄 발생 건수"
    if year:
        target_df = target_df[target_df['Year'] == year]
        plot_title = f"인천시 {year}년 구별 총 범죄 발생 건수"
        if target_df.empty:
            print(f"오류: {year}년 데이터가 없습니다.")
            return


    district_cases = target_df.groupby('District')['Cases'].sum().sort_values(ascending=False)

    if district_cases.empty:
        print("시각화할 데이터가 없습니다.")
        return

    plt.figure(figsize=(12, 7))
    sns.barplot(x=district_cases.index, y=district_cases.values, palette="viridis")
    plt.title(plot_title, fontsize=16)
    plt.xlabel("구 (District)", fontsize=12)
    plt.ylabel("총 범죄 발생 건수 (Cases)", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # from file_reader import load_crime_data
    # from data_cleaner import clean_data
    # raw_data = load_crime_data('incheon_crime_data.csv')
    # cleaned_data = clean_data(raw_data)
    # if cleaned_data is not None:
    #     plot_total_crimes_by_district(cleaned_data, year=2023)
    #     # plot_total_crimes_by_district(cleaned_data) # 전체 연도 합산

    # 임시 데이터프레임으로 테스트
    sample_data = pd.DataFrame({
        'Year': [2023, 2023, 2023, 2022, 2022, 2023],
        'District': ['중구', '미추홀구', '연수구', '미추홀구', '중구', '남동구'],
        'CrimeType': ['절도', '폭력', '강도', '절도', '절도', '폭력'],
        'Cases': [100, 200, 50, 150, 80, 250],
    })
    plot_total_crimes_by_district(sample_data, year=2023)
