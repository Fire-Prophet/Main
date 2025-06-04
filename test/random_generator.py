# random_generator.py
import random
import string
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_random_integer(min_val, max_val):
    """
    지정된 범위 내의 무작위 정수를 생성합니다 (양 끝 포함).
    """
    if not isinstance(min_val, int) or not isinstance(max_val, int):
        logging.error("min_val and max_val must be integers.")
        raise TypeError("min_val and max_val must be integers.")
    if min_val > max_val:
        logging.error(f"min_val ({min_val}) cannot be greater than max_val ({max_val}).")
        raise ValueError("min_val cannot be greater than max_val.")

    rand_int = random.randint(min_val, max_val)
    logging.info(f"Generated random integer between {min_val} and {max_val}: {rand_int}")
    return rand_int

def generate_random_float(min_val, max_val):
    """
    지정된 범위 내의 무작위 부동 소수점 숫자를 생성합니다.
    """
    if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
        logging.error("min_val and max_val must be numbers.")
        raise TypeError("min_val and max_val must be numbers.")
    if min_val > max_val:
        logging.error(f"min_val ({min_val}) cannot be greater than max_val ({max_val}).")
        raise ValueError("min_val cannot be greater than max_val.")

    rand_float = random.uniform(min_val, max_val)
    logging.info(f"Generated random float between {min_val} and {max_val}: {rand_float}")
    return rand_float

def generate_random_string(length, chars=None):
    """
    지정된 길이의 무작위 문자열을 생성합니다.
    chars가 지정되지 않으면 ASCII 대소문자, 숫자, 구두점을 사용합니다.
    """
    if not isinstance(length, int) or length < 0:
        logging.error("Length must be a non-negative integer.")
        raise ValueError("Length must be a non-negative integer.")

    if chars is None:
        chars = string.ascii_letters + string.digits + string.punctuation
    
    if not chars:
        logging.warning("Character set for random string is empty. Returning empty string.")
        return ""

    random_str = ''.join(random.choice(chars) for _ in range(length))
    logging.info(f"Generated random string of length {length}.")
    return random_str

def select_random_element(input_list):
    """
    리스트에서 무작위 요소를 선택합니다.
    """
    if not isinstance(input_list, list):
        logging.error("Input must be a list.")
        raise TypeError("Input must be a list.")
    if not input_list:
        logging.warning("Input list is empty. Cannot select a random element.")
        return None

    selected_element = random.choice(input_list)
    logging.info(f"Selected random element from list: {selected_element}")
    return selected_element

# 예시 사용
if __name__ == "__main__":
    print(f"Random integer (1-100): {generate_random_integer(1, 100)}")
    print(f"Random float (0.0-1.0): {generate_random_float(0.0, 1.0):.4f}")
    print(f"Random string (15 chars): {generate_random_string(15)}")
    print(f"Random password (10 chars, digits only): {generate_random_string(10, string.digits)}")

    fruits = ["apple", "banana", "cherry", "date"]
    print(f"Random fruit: {select_random_element(fruits)}")

    try:
        # 에러 발생 예시
        # generate_random_integer(10, 5)
        # select_random_element(123)
        pass
    except (ValueError, TypeError) as e:
        print(f"Caught expected error: {e}")
