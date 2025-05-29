# filename: filter_by_year_district.py
import pandas as pd

def filter_data(df, year=None, district=None):
    """
    주어진 연도 및/또는 구(District)로 데이터를 필터링합니다.
    """
    if df is None:
        return None

    filtered_df = df.copy()
    if year:
        # 'Year' 컬럼이 숫자형이라고 가정
        filtered_df = filtered_df[filtered_df['Year'] == int(year)]
    if district:
        filtered_df = filtered_df[filtered_df['District'] == district]

    print(f"\n필터링 조건: Year={year}, District={district}")
    print(f"필터링된 데이터 {len(filtered_df)}건:")
    print(filtered_df)
    return filtered_df

if __name__ == '__main__':
    # 예시 사용법 (file_reader.py, data_cleaner.py 함수 사용 가정)
    # from file_reader import load_crime_data
    # from data_cleaner import clean_data
    # raw_data = load_crime_data('incheon_crime_data.csv')
    # cleaned_data = clean_data(raw_data)
    # if cleaned_data is not None:
    #     filtered_result = filter_data(cleaned_data, year=2023, district='미추홀구')

    # 임시 데이터프레임으로 테스트
    sample_data = pd.DataFrame({
        'Year': [2023, 2023, 2022, 2023],
        'District': ['중구', '미추홀구', '중구', '미추홀구'],
        'CrimeType': ['절도', '폭력', '절도', '절도'],
        'Cases': [500, 700, 450, 200],
    })
    filtered = filter_data(sample_data, year=2023, district='미추홀구')
