# filename: yearly_trend_district.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정 (위의 plot_crimes_per_district.py와 동일하게 설정)
try:
    import platform
    if platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    elif platform.system() == 'Darwin': # macOS
        plt.rc('font', family='AppleGothic')
    else: # Linux
        plt.rc('font', family='NanumGothic')
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    print(f"폰트 설정 중 오류: {e}. 기본 폰트로 진행합니다.")

def plot_yearly_crime_trend(df, district, crime_type):
    """
    특정 구(district)에서 특정 범죄 유형(crime_type)의 연도별 발생 건수 추이를 시각화합니다.
    """
    if df is None or 'Year' not in df.columns or 'District' not in df.columns or \
       'CrimeType' not in df.columns or 'Cases' not in df.columns:
        print("오류: 필요한 컬럼이 데이터에 없습니다.")
        return

    trend_data = df[
        (df['District'] == district) & (df['CrimeType'] == crime_type)
    ].copy() # Use .copy()

    if trend_data.empty:
        print(f"'{district}'의 '{crime_type}'에 대한 데이터가 없습니다.")
        return

    # 'Year' 컬럼을 숫자형으로 변환 (이미 되어있다면 생략 가능)
    trend_data.loc[:, 'Year'] = pd.to_numeric(trend_data['Year'], errors='coerce')
    trend_data = trend_data.dropna(subset=['Year']) # Year 변환 실패 시 NaN 제거
    trend_data = trend_data.sort_values(by='Year')


    plt.figure(figsize=(10, 6))
    sns.lineplot(x='Year', y='Cases', data=trend_data, marker='o', errorbar=None) # errorbar=None to remove confidence interval
    plt.title(f"'{district}' {crime_type} 연도별 발생 건수 추이", fontsize=15)
    plt.xlabel("연도 (Year)", fontsize=12)
    plt.ylabel("발생 건수 (Cases)", fontsize=12)
    plt.xticks(trend_data['Year'].unique().astype(int)) # 정수형 연도만 표시
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # from file_reader import load_crime_data
    # from data_cleaner import clean_data
    # raw_data = load_crime_data('incheon_crime_data.csv')
    # cleaned_data = clean_data(raw_data)
    # if cleaned_data is not None:
    #     plot_yearly_crime_trend(cleaned_data, district='미추홀구', crime_type='절도')

    # 임시 데이터프레임으로 테스트
    sample_data = pd.DataFrame({
        'Year': [2020, 2021, 2022, 2023, 2020, 2021, 2022, 2023],
        'District': ['미추홀구', '미추홀구', '미추홀구', '미추홀구', '중구', '중구', '중구', '중구'],
        'CrimeType': ['절도', '절도', '절도', '절도', '절도', '절도', '절도', '절도'],
        'Cases': [180, 160, 150, 170, 90, 80, 70, 85],
    })
    plot_yearly_crime_trend(sample_data, district='미추홀구', crime_type='절도')
