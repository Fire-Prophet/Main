# data_processor.py
import pandas as pd
import numpy as np
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataProcessor:
    def __init__(self, data):
        """
        데이터 처리 클래스 초기화.
        """
        self.data = pd.DataFrame(data)
        logging.info("DataProcessor initialized with new data.")

    def clean_data(self):
        """
        결측치를 제거하고 중복을 처리합니다.
        """
        original_rows = len(self.data)
        self.data.dropna(inplace=True)
        self.data.drop_duplicates(inplace=True)
        cleaned_rows = len(self.data)
        logging.info(f"Data cleaned. Removed {original_rows - cleaned_rows} rows.")
        return self.data

    def summarize_data(self):
        """
        데이터의 기본 통계 요약을 반환합니다.
        """
        summary = self.data.describe()
        logging.info("Data summary generated.")
        return summary

    def add_random_column(self, col_name="random_value"):
        """
        데이터프레임에 무작위 값으로 새 열을 추가합니다.
        """
        self.data[col_name] = np.random.rand(len(self.data))
        logging.info(f"Added new column: {col_name}")
        return self.data

# 예시 사용
if __name__ == "__main__":
    sample_data = {
        'col1': [1, 2, np.nan, 4, 5, 1],
        'col2': ['A', 'B', 'C', 'D', 'E', 'A'],
        'col3': [10.1, 12.5, 11.3, 15.0, np.nan, 10.1]
    }
    processor = DataProcessor(sample_data)
    cleaned_df = processor.clean_data()
    print("Cleaned Data:\n", cleaned_df)
    summary_df = processor.summarize_data()
    print("\nData Summary:\n", summary_df)
    extended_df = processor.add_random_column()
    print("\nExtended Data:\n", extended_df)
