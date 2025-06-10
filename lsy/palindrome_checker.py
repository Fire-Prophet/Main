def is_palindrome(text):
    cleaned = ''.join(filter(str.isalnum, text.lower()))
    return cleaned == cleaned[::-1]

s = input("문장을 입력하세요: ")
print("회문입니다." if is_palindrome(s) else "회문이 아닙니다.")
