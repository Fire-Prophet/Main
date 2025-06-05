# password_generator.py
import random
import string

def generate_password(length=12, use_uppercase=True, use_lowercase=True, use_digits=True, use_symbols=True):
    """
    지정된 조건에 따라 무작위 암호를 생성합니다.
    """
    character_pool = ""
    if use_uppercase:
        character_pool += string.ascii_uppercase
    if use_lowercase:
        character_pool += string.ascii_lowercase
    if use_digits:
        character_pool += string.digits
    if use_symbols:
        character_pool += string.punctuation # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

    if not character_pool:
        raise ValueError("암호 생성에 사용할 문자 유형이 선택되지 않았습니다.")

    # 최소한 각 유형의 문자가 하나씩 포함되도록 보장 (선택 사항)
    password_chars = []
    if use_uppercase:
        password_chars.append(random.choice(string.ascii_uppercase))
    if use_lowercase:
        password_chars.append(random.choice(string.ascii_lowercase))
    if use_digits:
        password_chars.append(random.choice(string.digits))
    if use_symbols:
        password_chars.append(random.choice(string.punctuation))
    
    # 남은 길이만큼 character_pool에서 무작위로 선택
    remaining_length = length - len(password_chars)
    if remaining_length < 0: # 요청 길이가 너무 짧을 경우, 보장된 문자만으로 구성
        password_chars = password_chars[:length]
        remaining_length = 0

    for _ in range(remaining_length):
        password_chars.append(random.choice(character_pool))
    
    # 생성된 암호를 섞음
    random.shuffle(password_chars)
    
    return "".join(password_chars)

def main():
    """암호 생성기 메인 함수"""
    print("암호 생성기입니다.")
    
    while True:
        try:
            length = int(input("원하는 암호 길이를 입력하세요 (최소 8자): "))
            if length < 8:
                print("암호 길이는 최소 8자 이상이어야 합니다.")
                continue
            break
        except ValueError:
            print("숫자를 입력해주세요.")

    use_upper = input("대문자를 포함할까요? (yes/no): ").lower() == 'yes'
    use_lower = input("소문자를 포함할까요? (yes/no): ").lower() == 'yes'
    use_nums = input("숫자를 포함할까요? (yes/no): ").lower() == 'yes'
    use_syms = input("특수문자를 포함할까요? (yes/no): ").lower() == 'yes'

    if not (use_upper or use_lower or use_nums or use_syms):
        print("적어도 하나의 문자 유형을 선택해야 합니다. 기본값으로 소문자와 숫자를 사용합니다.")
        use_lower = True
        use_nums = True

    try:
        password = generate_password(length, use_upper, use_lower, use_nums, use_syms)
        print(f"\n생성된 암호: {password}")
    except ValueError as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    main()
