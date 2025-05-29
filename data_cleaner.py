# filename: data_cleaner.py
import pandas as pd

def clean_data(df):
    """
    범죄 데이터프레임의 기본적인 클리닝을 수행합니다.
    """
    if df is None:
        return None

    print("\n데이터 클리닝 시작...")
    # 결측치가 있는 행 제거 (또는 다른 방식으로 처리, 예: df.fillna(0, inplace=True))
    df_cleaned = df.dropna().copy() # Use .copy() to avoid SettingWithCopyWarning
    print(f"결측치 제거 후 {len(df_cleaned)}개의 행이 남았습니다.")

    # 데이터 타입 변환 (예시: 'Year'를 정수형으로)
    # 실제 데이터에 맞게 열 이름과 타입을 수정하세요.
    if 'Year' in df_cleaned.columns:
        df_cleaned.loc[:, 'Year'] = pd.to_numeric(df_cleaned['Year'], errors='coerce')
    if 'Cases' in df_cleaned.columns:
        df_cleaned.loc[:, 'Cases'] = pd.to_numeric(df_cleaned['Cases'], errors='coerce')
    if 'Arrests' in df_cleaned.columns:
        df_cleaned.loc[:, 'Arrests'] = pd.to_numeric(df_cleaned['Arrests'], errors='coerce')
    if 'Population' in df_cleaned.columns:
        df_cleaned.loc[:, 'Population'] = pd.to_numeric(df_cleaned['Population'], errors='coerce')

    # 불필요한 공백 제거 (예시: 'District' 열)
    if 'District' in df_cleaned.columns:
        df_cleaned.loc[:, 'District'] = df_cleaned['District'].str.strip()
    if 'CrimeType' in df_cleaned.columns:
        df_cleaned.loc[:, 'CrimeType'] = df_cleaned['CrimeType'].str.strip()

    print("데이터 타입 변환 및 공백 제거 완료.")
    print("클리닝된 데이터 정보:")
    df_cleaned.info()
    return df_cleaned

if __name__ == '__main__':
    # 예시 사용법 (file_reader.py의 함수 사용 가정)
    # from file_reader import load_crime_data
    # raw_data = load_crime_data('incheon_crime_data.csv')
    # cleaned_data = clean_data(raw_data)
    # if cleaned_data is not None:
    #     print("\n클리닝된 데이터 샘플:")
    #     print(cleaned_data.head())

    # 임시 데이터프레임으로 테스트
    sample_data = pd.DataFrame({
        'Year': ['2023', '2023', None, '2022'],
        'District': [' 중구 ', '미추홀구', '연수구', '남동구 '],
        'CrimeType': ['절도', '폭력', '강도', '절도'],
        'Cases': ['500', '700', '50', '450a'], # '450a' is intentionally non-numeric
        'Arrests': [300, 550, 30, 280],
        'Population': [150000, 400000, 350000, 530000]
    })
    cleaned = clean_data(sample_data.copy()) # Pass a copy for safety
    if cleaned is not None:
        print("\n클리닝된 데이터 샘플:")
        print(cleaned.head())
