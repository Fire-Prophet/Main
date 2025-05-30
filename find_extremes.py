# filename: find_extremes.py
import pandas as pd

def find_crime_extremes(df, year=None):
    """
    범죄 발생 건수가 가장 높은 구와 가장 낮은 구를 찾습니다.
    특정 연도(year)가 주어지면 해당 연도의 데이터만 사용합니다.
    """
    if df is None or 'District' not in df.columns or 'Cases' not in df.columns:
        print("오류: 'District' 또는 'Cases' 컬럼이 데이터에 없습니다.")
        return None, None

    target_df = df.copy()
    context = "전체 기간"
    if year:
        target_df = target_df[target_df['Year'] == year]
        context = f"{year}년"
        if target_df.empty:
            print(f"오류: {year}년 데이터가 없습니다.")
            return None, None

    district_total_cases = target_df.groupby('District')['Cases'].sum()

    if district_total_cases.empty:
        print(f"{context} 데이터가 없어 극값을 찾을 수 없습니다.")
        return None, None

    highest_crime_district = district_total_cases.idxmax()
    lowest_crime_district = district_total_cases.idxmin()

    highest_cases = district_total_cases.max()
    lowest_cases = district_total_cases.min()

    print(f"\n{context} 범죄 발생 건수 극값:")
    print(f"  가장 높은 구: {highest_crime_district} (총 {highest_cases}건)")
    print(f"  가장 낮은 구: {lowest_crime_district} (총 {lowest_cases}건)")

    return (highest_crime_district, highest_cases), (lowest_crime_district, lowest_cases)

if __name__ == '__main__':
    # from file_reader import load_crime_data
    # from data_cleaner import clean_data
    # raw_data = load_crime_data('incheon_crime_data.csv')
    # cleaned_data = clean_data(raw_data)
    # if cleaned_data is not None:
    #     find_crime_extremes(cleaned_data, year=2023)
    #     find_crime_extremes(cleaned_data) # 전체 기간

    # 임시 데이터프레임으로 테스트
    sample_data = pd.DataFrame({
        'Year': [2023, 2023, 2023, 2022, 2022, 2023],
        'District': ['중구', '미추홀구', '연수구', '미추홀구', '중구', '남동구'],
        'CrimeType': ['절도', '폭력', '강도', '절도', '절도', '폭력'],
        'Cases': [100, 200, 50, 150, 80, 250],
    })
    find_crime_extremes(sample_data, year=2023)
