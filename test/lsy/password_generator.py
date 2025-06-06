import random
import string

def generate_password(length=10):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

print("생성된 비밀번호:", generate_password(12))
