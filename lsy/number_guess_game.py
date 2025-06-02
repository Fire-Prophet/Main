import random
target = random.randint(1, 100)
while True:
    guess = int(input("숫자 맞히기 (1~100): "))
    if guess < target:
        print("더 큰 수입니다.")
    elif guess > target:
        print("더 작은 수입니다.")
    else:
        print("정답!")
        break
