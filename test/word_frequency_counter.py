# word_frequency_counter.py
import string
from collections import Counter

def clean_word(word):
    """단어에서 구두점을 제거하고 소문자로 변환합니다."""
    # 앞뒤 구두점만 제거 (단어 중간의 하이픈 등은 유지)
    cleaned = word.strip(string.punctuation).lower()
    return cleaned

def count_word_frequencies(file_path):
    """
    텍스트 파일에서 단어 빈도를 계산합니다.
    :param file_path: 분석할 텍스트 파일 경로
    :return: 단어 빈도수를 담은 Counter 객체, 또는 오류 시 None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
    except FileNotFoundError:
        print(f"오류: 파일 '{file_path}'를 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"파일 읽기 중 오류 발생: {e}")
        return None

    # 단어를 공백 기준으로 분리
    words = text_content.split()
    
    cleaned_words = [clean_word(word) for word in words if clean_word(word)] # 빈 문자열 제거
    
    if not cleaned_words:
        print("파일에 분석할 단어가 없습니다.")
        return Counter() # 비어있는 Counter 객체 반환

    word_counts = Counter(cleaned_words)
    return word_counts

def display_top_words(word_counts, top_n=10):
    """가장 빈번하게 등장하는 단어들을 출력합니다."""
    if not word_counts:
        print("표시할 단어 빈도 정보가 없습니다.")
        return
        
    print(f"\n--- 상위 {top_n} 단어 빈도 ---")
    # most_common()은 (단어, 빈도수) 튜플의 리스트를 반환
    for word, count in word_counts.most_common(top_n):
        print(f"'{word}': {count}회")
    print("------------------------")

def main():
    """단어 빈도 분석기 메인 함수"""
    print("텍스트 파일 단어 빈도 분석기입니다.")
    file_path = input("분석할 텍스트 파일의 경로를 입력하세요: ")

    if not file_path:
        print("파일 경로가 입력되지 않았습니다. 'sample_text.txt'를 생성하여 테스트합니다.")
        file_path = "sample_text.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("This is a sample text. This text is for testing purposes.\n")
            f.write("Hello world, hello Python. Python is fun, and Python is powerful.")
    
    frequencies = count_word_frequencies(file_path)
    
    if frequencies is not None: # 오류 없이 Counter 객체를 받은 경우
        num_top_words_str = input("출력할 상위 단어 개수를 입력하세요 (기본값 10): ")
        try:
            num_top_words = int(num_top_words_str) if num_top_words_str else 10
            if num_top_words <= 0:
                num_top_words = 10 # 잘못된 입력 시 기본값
        except ValueError:
            num_top_words = 10 # 숫자가 아닌 입력 시 기본값
            
        display_top_words(frequencies, num_top_words)
        
        # 추가 분석 (예: 총 단어 수, 고유 단어 수)
        total_words = sum(frequencies.values())
        unique_words = len(frequencies)
        print(f"\n총 단어 수: {total_words}")
        print(f"고유 단어 수: {unique_words}")

if __name__ == "__main__":
    main()
