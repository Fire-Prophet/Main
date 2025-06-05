# filename: aggregate_crime_types.py
import pandas as pd

def aggregate_by_crimetype(df, district=None):
    """
    범죄 유형별 총 발생 건수를 집계합니다.
    특정 구(district)가 주어지면 해당 구의 데이터만 집계합니다.
    """
    if df is None:
        return None

    target_df = df.copy()
    title_prefix = "전체 지역"
    if district:
        target_df = target_df[target_df['District'] == district]
        title_prefix = f"'{district}'"
        if target_df.empty:
            print(f"오류: '{district}'에 대한 데이터가 없습니다.")
            return None

    crime_type_summary = target_df.groupby('CrimeType')['Cases'].sum().reset_index()
    crime_type_summary = crime_type_summary.sort_values(by='Cases', ascending=False)

    print(f"\n{title_prefix} 범죄 유형별 총 발생 건수:")
    print(crime_type_summary)
    return crime_type_summary

if __name__ == '__main__':
    # from file_reader import load_crime_data
    # from data_cleaner import clean_data
    # raw_data = load_crime_data('incheon_crime_data.csv')
    # cleaned_data = clean_data(raw_data)
    # if cleaned_data is not None:
    #     # 2023년 데이터만 필터링
    #     data_2023 = cleaned_data[cleaned_data['Year'] == 2023]
    #     aggregate_by_crimetype(data_2023, district='미추홀구')
    #     aggregate_by_crimetype(data_2023) # 전체 지역

    # 임시 데이터프레임으로 테스트
    sample_data = pd.DataFrame({
        'Year': [2023, 2023, 2023, 2023, 2022],
        'District': ['중구', '미추홀구', '중구', '미추홀구', '중구'],
        'CrimeType': ['절도', '폭력', '폭력', '절도', '절도'],
        'Cases': [100, 200, 50, 120, 80],
    })
    # 2023년 데이터만 사용
    sample_data_2023 = sample_data[sample_data['Year'] == 2023]
    aggregate_by_crimetype(sample_data_2023, district='미추홀구')
    aggregate_by_crimetype(sample_data_2023)
