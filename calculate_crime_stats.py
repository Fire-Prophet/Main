# filename: calculate_crime_stats.py
import pandas as pd

def calculate_district_crime_stats(df):
    """
    구별 총 범죄 건수 및 인구 10만 명당 범죄율을 계산합니다.
    'Population' 컬럼이 필요합니다.
    """
    if df is None or 'District' not in df.columns or 'Cases' not in df.columns:
        print("오류: 'District' 또는 'Cases' 컬럼이 데이터에 없습니다.")
        return None
    if 'Population' not in df.columns:
        print("경고: 'Population' 컬럼이 없어 인구당 범죄율 계산이 불가능합니다. 총 건수만 계산합니다.")
        district_stats = df.groupby('District')['Cases'].sum().reset_index()
        district_stats.rename(columns={'Cases': 'TotalCases'}, inplace=True)
        return district_stats.sort_values(by='TotalCases', ascending=False)

    # 구별 총 범죄 건수 및 평균 인구 계산
    # 동일 연도 내에서 구별 인구가 같다면 first() 사용, 아니라면 평균 등 다른 집계 방식 고려
    district_summary = df.groupby('District').agg(
        TotalCases=('Cases', 'sum'),
        Population=('Population', 'first') # 또는 'mean' 등
    ).reset_index()

    # 인구 10만명 당 범죄 발생률 계산
    # Population이 0인 경우를 대비하여 오류 처리
    district_summary['CrimeRatePer100K'] = district_summary.apply(
        lambda row: (row['TotalCases'] / row['Population']) * 100000 if row['Population'] > 0 else 0, axis=1
    )

    print("\n구별 범죄 통계 (총 건수, 인구 10만명 당 발생률):")
    print(district_summary.sort_values(by='CrimeRatePer100K', ascending=False))
    return district_summary

if __name__ == '__main__':
    # 예시 사용법
    # from file_reader import load_crime_data
    # from data_cleaner import clean_data
    # raw_data = load_crime_data('incheon_crime_data.csv')
    # cleaned_data = clean_data(raw_data)
    # if cleaned_data is not None:
    #     # 특정 연도 데이터로 필터링 후 통계 계산
    #     data_2023 = cleaned_data[cleaned_data['Year'] == 2023]
    #     stats = calculate_district_crime_stats(data_2023)

    # 임시 데이터프레임으로 테스트
    sample_data = pd.DataFrame({
        'Year': [2023, 2023, 2023, 2022, 2022],
        'District': ['중구', '미추홀구', '중구', '미추홀구', '중구'],
        'CrimeType': ['절도', '폭력', '폭력', '절도', '절도'],
        'Cases': [100, 200, 50, 150, 80],
        'Population': [150000, 400000, 150000, 390000, 148000] # 중복된 구에 대해 인구는 같다고 가정
    })
    # 2023년 데이터만 사용
    sample_data_2023 = sample_data[sample_data['Year'] == 2023]
    crime_stats = calculate_district_crime_stats(sample_data_2023)
