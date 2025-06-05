# caesar_cipher.py

def caesar_cipher(text, shift, mode='encrypt'):
    """
    카이사르 암호화 또는 복호화를 수행합니다.
    :param text: 암호화/복호화할 문자열
    :param shift: 이동할 칸 수 (정수)
    :param mode: 'encrypt' 또는 'decrypt'
    :return: 결과 문자열
    """
    result = ''
    
    # 복호화 시 shift 값을 반대로 적용
    if mode == 'decrypt':
        shift = -shift
        
    for char in text:
        if 'a' <= char <= 'z':
            # 소문자 처리
            start = ord('a')
            shifted_char = chr((ord(char) - start + shift) % 26 + start)
        elif 'A' <= char <= 'Z':
            # 대문자 처리
            start = ord('A')
            shifted_char = chr((ord(char) - start + shift) % 26 + start)
        else:
            # 알파벳이 아닌 경우 그대로 유지
            shifted_char = char
        result += shifted_char
        
    return result

def main():
    """카이사르 암호 프로그램 메인 함수"""
    print("카이사르 암호 프로그램입니다.")

    while True:
        action = input("원하는 작업을 선택하세요 (encrypt/decrypt/quit): ").lower()
        if action == 'quit':
            print("프로그램을 종료합니다.")
            break
        
        if action not in ['encrypt', 'decrypt']:
            print("잘못된 작업입니다. 'encrypt', 'decrypt', 'quit' 중 하나를 입력하세요.")
            continue

        message = input("메시지를 입력하세요: ")
        
        while True:
            try:
                key = int(input("이동할 칸 수 (정수)를 입력하세요: "))
                break
            except ValueError:
                print("숫자를 입력해주세요.")
        
        if action == 'encrypt':
            encrypted_message = caesar_cipher(message, key, mode='encrypt')
            print(f"암호화된 메시지: {encrypted_message}")
        elif action == 'decrypt':
            decrypted_message = caesar_cipher(message, key, mode='decrypt')
            print(f"복호화된 메시지: {decrypted_message}")
            
        print("-" * 20)

if __name__ == "__main__":
    main()
