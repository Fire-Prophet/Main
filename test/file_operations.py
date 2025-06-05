# file_operations.py
import os
import shutil
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_directory(path):
    """
    주어진 경로에 디렉토리를 생성합니다. 이미 존재하면 아무것도 하지 않습니다.
    """
    try:
        os.makedirs(path, exist_ok=True)
        logging.info(f"Directory created or already exists: {path}")
        return True
    except OSError as e:
        logging.error(f"Error creating directory {path}: {e}")
        return False

def write_to_file(filepath, content, mode='w'):
    """
    주어진 파일 경로에 내용을 씁니다.
    mode: 'w' (쓰기, 덮어쓰기), 'a' (추가)
    """
    try:
        with open(filepath, mode, encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Content written to file: {filepath} in mode '{mode}'")
        return True
    except IOError as e:
        logging.error(f"Error writing to file {filepath}: {e}")
        return False

def read_from_file(filepath):
    """
    주어진 파일에서 내용을 읽어 반환합니다.
    """
    if not os.path.exists(filepath):
        logging.warning(f"File not found: {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        logging.info(f"Content read from file: {filepath}")
        return content
    except IOError as e:
        logging.error(f"Error reading from file {filepath}: {e}")
        return None

def delete_file(filepath):
    """
    주어진 파일을 삭제합니다.
    """
    if os.path.exists(filepath) and os.path.isfile(filepath):
        try:
            os.remove(filepath)
            logging.info(f"File deleted: {filepath}")
            return True
        except OSError as e:
            logging.error(f"Error deleting file {filepath}: {e}")
            return False
    logging.warning(f"File not found or is not a file: {filepath}")
    return False

# 예시 사용
if __name__ == "__main__":
    test_dir = "test_files"
    create_directory(test_dir)

    test_file_path = os.path.join(test_dir, "sample.txt")
    write_to_file(test_file_path, "Hello, this is a test line.\n")
    write_to_file(test_file_path, "This is another line.", mode='a')

    read_content = read_from_file(test_file_path)
    if read_content:
        print(f"Content of {test_file_path}:\n{read_content}")

    delete_file(test_file_path)

    # 디렉토리 삭제 (선택 사항)
    # try:
    #     shutil.rmtree(test_dir)
    #     logging.info(f"Directory removed: {test_dir}")
    # except OSError as e:
    #     logging.error(f"Error removing directory {test_dir}: {e}")
