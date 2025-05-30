import random
import string
import argparse

def generate_password(length=12, use_upper=True, use_lower=True, use_digits=True, use_special=True):
    """지정된 조건에 맞는 안전한 비밀번호를 생성합니다."""
    
    characters = ""
    if use_upper:
        characters += string.ascii_uppercase
    if use_lower:
        characters += string.ascii_lowercase
    if use_digits:
        characters += string.digits
    if use_special:
        characters += string.punctuation

    if not characters:
        return "오류: 비밀번호에 사용할 문자 유형을 하나 이상 선택해야 합니다."

    while True:
        password = ''.join(random.choice(characters) for _ in range(length))
        
        # 각 유형이 최소 하나 이상 포함되었는지 확인 (선택 사항)
        has_upper = not use_upper or any(c in string.ascii_uppercase for c in password)
        has_lower = not use_lower or any(c in string.ascii_lowercase for c in password)
        has_digit = not use_digits or any(c in string.digits for c in password)
        has_special = not use_special or any(c in string.punctuation for c in password)

        if has_upper and has_lower and has_digit and has_special:
            return password

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="안전한 비밀번호를 생성합니다.")
    parser.add_argument("-l", "--length", type=int, default=16, help="비밀번호 길이 (기본값: 16)")
    parser.add_argument("--no-upper", action="store_false", help="대문자 미포함", dest="use_upper")
    parser.add_argument("--no-lower", action="store_false", help="소문자 미포함", dest="use_lower")
    parser.add_argument("--no-digits", action="store_false", help="숫자 미포함", dest="use_digits")
    parser.add_argument("--no-special", action="store_false", help="특수문자 미포함", dest="use_special")
    
    args = parser.parse_args()

    if args.length < 4:
        print("오류: 비밀번호 길이는 4자 이상이어야 합니다.")
    else:
        new_password = generate_password(
            length=args.length,
            use_upper=args.use_upper,
            use_lower=args.use_lower,
            use_digits=args.use_digits,
            use_special=args.use_special
        )
        print(f"생성된 비밀번호: {new_password}")
