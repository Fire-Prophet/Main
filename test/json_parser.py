# json_parser.py
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_json_string(json_string):
    """
    JSON 문자열을 Python 객체로 파싱합니다.
    """
    try:
        data = json.loads(json_string)
        logging.info("JSON string successfully parsed.")
        return data
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON string: {e}")
        return None

def serialize_python_object(obj, indent=None):
    """
    Python 객체를 JSON 문자열로 직렬화합니다.
    """
    try:
        json_string = json.dumps(obj, indent=indent, ensure_ascii=False)
        logging.info("Python object successfully serialized to JSON.")
        return json_string
    except TypeError as e:
        logging.error(f"Error serializing Python object to JSON: {e}")
        return None

def load_json_from_file(filepath):
    """
    파일에서 JSON 데이터를 로드합니다.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"JSON data loaded from file: {filepath}")
        return data
    except FileNotFoundError:
        logging.error(f"JSON file not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from file {filepath}: {e}")
        return None

def save_json_to_file(filepath, data, indent=4):
    """
    Python 객체를 JSON 형식으로 파일에 저장합니다.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logging.info(f"JSON data saved to file: {filepath}")
        return True
    except TypeError as e:
        logging.error(f"Error saving data to JSON file {filepath}: {e}")
        return False
    except IOError as e:
        logging.error(f"File I/O error saving JSON to {filepath}: {e}")
        return False

# 예시 사용
if __name__ == "__main__":
    test_json_string = '{"name": "김철수", "age": 30, "isStudent": false, "courses": ["Math", "Science"]}'
    parsed_data = parse_json_string(test_json_string)
    if parsed_data:
        print("Parsed Data:", parsed_data)
        print("Name:", parsed_data.get('name'))

    test_python_object = {
        "product": "Laptop",
        "price": 1200.50,
        "features": ["16GB RAM", "512GB SSD"],
        "available": True
    }
    json_output = serialize_python_object(test_python_object, indent=2)
    if json_output:
        print("\nSerialized JSON:\n", json_output)

    # 파일 관련 예시
    file_path = "sample_data.json"
    save_json_to_file(file_path, test_python_object)
    loaded_data = load_json_from_file(file_path)
    if loaded_data:
        print("\nLoaded data from file:", loaded_data)

    # 생성된 파일 삭제
    # import os
    # if os.path.exists(file_path):
    #     os.remove(file_path)
    #     logging.info(f"Cleaned up {file_path}")
