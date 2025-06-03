import random

secret = random.randint(1, 100)
attempts = 0

while True:
    guess = int(input("1~100 사이의 숫자를 맞춰보세요: "))
    attempts += 1
    if guess < secret:
        print("너무 작아요.")
    elif guess > secret:
        print("너무 커요.")
    else:
        print(f"정답! {attempts}번 만에 맞췄어요.")
        break
