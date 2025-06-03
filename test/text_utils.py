# text_utils.py
import re
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def reverse_string(s):
    """
    주어진 문자열을 뒤집습니다.
    """
    if not isinstance(s, str):
        logging.error(f"Input is not a string: {type(s)}")
        raise TypeError("Input must be a string.")
    reversed_s = s[::-1]
    logging.info(f"Reversed string '{s}' to '{reversed_s}'")
    return reversed_s

def count_words(text):
    """
    주어진 텍스트의 단어 수를 계산합니다.
    """
    if not isinstance(text, str):
        logging.error(f"Input is not a string: {type(text)}")
        raise TypeError("Input must be a string.")
    words = re.findall(r'\b\w+\b', text.lower())
    count = len(words)
    logging.info(f"Counted {count} words in text.")
    return count

def is_palindrome(text):
    """
    주어진 텍스트가 회문(palindrome)인지 확인합니다.
    공백과 구두점은 무시하고 대소문자를 구분하지 않습니다.
    """
    if not isinstance(text, str):
        logging.error(f"Input is not a string: {type(text)}")
        raise TypeError("Input must be a string.")
    clean_text = ''.join(filter(str.isalnum, text)).lower()
    result = clean_text == clean_text[::-1]
    logging.info(f"Checked if '{text}' is a palindrome: {result}")
    return result

def remove_vowels(text):
    """
    주어진 텍스트에서 모음을 제거합니다.
    """
    if not isinstance(text, str):
        logging.error(f"Input is not a string: {type(text)}")
        raise TypeError("Input must be a string.")
    vowels = "aeiouAEIOU"
    result_text = "".join([char for char in text if char not in vowels])
    logging.info(f"Removed vowels from text.")
    return result_text

# 예시 사용
if __name__ == "__main__":
    print(f"Reversed 'hello': {reverse_string('hello')}")
    print(f"Word count of 'Hello world, how are you?': {count_words('Hello world, how are you?')}")
    print(f"'Madam' is palindrome: {is_palindrome('Madam')}")
    print(f"'Python' is palindrome: {is_palindrome('Python')}")
    print(f"Removed vowels from 'Programming': {remove_vowels('Programming')}")
