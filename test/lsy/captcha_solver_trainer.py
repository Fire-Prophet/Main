import random
import string

def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

captcha = generate_captcha()
print("CAPTCHA:", captcha)
answer = input("위 문자를 입력하세요: ")

if answer == captcha:
    print("정답입니다! ✅")
else:
    print("틀렸어요. 다시 시도해보세요. ❌")
