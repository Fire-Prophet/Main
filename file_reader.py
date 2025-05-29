# filename: file_reader.py
import pandas as pd

def load_crime_data(file_path):
    """
    CSV 파일에서 범죄 데이터를 로드합니다.
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8') # 또는 'cp949' for Korean Windows Excel files
        print(f"'{file_path}'에서 데이터를 성공적으로 로드했습니다.")
        print("데이터 샘플:")
        print(df.head())
        return df
    except FileNotFoundError:
        print(f"오류: 파일 '{file_path}'을(를) 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"데이터 로드 중 오류 발생: {e}")
        return None

if __name__ == '__main__':
    # 실제 파일 경로로 수정하세요.
    # 예시: data = load_crime_data('data/incheon_crime_data.csv')
    data = load_crime_data('incheon_crime_data.csv')
    if data is not None:
        print(f"\n총 {len(data)}개의 데이터 행이 로드되었습니다.")
