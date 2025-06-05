# csv_handler.py
import csv
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_csv_file(filepath):
    """
    주어진 CSV 파일에서 데이터를 읽어 리스트 오브 딕셔너리 형태로 반환합니다.
    """
    if not os.path.exists(filepath):
        logging.error(f"CSV file not found: {filepath}")
        return None
    data = []
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        logging.info(f"Successfully read data from {filepath}. {len(data)} rows found.")
        return data
    except Exception as e:
        logging.error(f"Error reading CSV file {filepath}: {e}")
        return None

def write_csv_file(filepath, data, fieldnames):
    """
    주어진 데이터를 CSV 파일에 씁니다.
    data: 리스트 오브 딕셔너리
    fieldnames: CSV 헤더로 사용할 필드명 리스트
    """
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"Successfully wrote {len(data)} rows to {filepath}.")
        return True
    except Exception as e:
        logging.error(f"Error writing to CSV file {filepath}: {e}")
        return False

def append_to_csv_file(filepath, data, fieldnames):
    """
    주어진 데이터를 기존 CSV 파일에 추가합니다. 파일이 없으면 새로 생성합니다.
    """
    file_exists = os.path.exists(filepath)
    try:
        with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader() # 파일이 없으면 헤더 쓰기
            writer.writerows(data)
        logging.info(f"Successfully appended {len(data)} rows to {filepath}.")
        return True
    except Exception as e:
        logging.error(f"Error appending to CSV file {filepath}: {e}")
        return False

# 예시 사용
if __name__ == "__main__":
    sample_data_write = [
        {'name': 'Alice', 'age': 30, 'city': 'New York'},
        {'name': 'Bob', 'age': 24, 'city': 'London'}
    ]
    sample_fieldnames = ['name', 'age', 'city']
    output_file = 'output.csv'

    write_csv_file(output_file, sample_data_write, sample_fieldnames)

    read_data = read_csv_file(output_file)
    if read_data:
        print("Read Data:")
        for row in read_data:
            print(row)

    sample_data_append = [
        {'name': 'Charlie', 'age': 35, 'city': 'Paris'},
        {'name': 'David', 'age': 29, 'city': 'Berlin'}
    ]
    append_to_csv_file(output_file, sample_data_append, sample_fieldnames)

    read_data_appended = read_csv_file(output_file)
    if read_data_appended:
        print("\nRead Data after append:")
        for row in read_data_appended:
            print(row)

    # 생성된 파일 삭제
    # if os.path.exists(output_file):
    #     os.remove(output_file)
    #     logging.info(f"Cleaned up {output_file}")
