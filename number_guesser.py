# number_guesser.py
import random

def play_guessing_game():
    """숫자 추측 게임을 실행하는 함수"""
    secret_number = random.randint(1, 100)
    attempts = 0
    max_attempts = 10

    print("숫자 추측 게임에 오신 것을 환영합니다!")
    print(f"1부터 100 사이의 숫자를 {max_attempts}번 안에 맞춰보세요.")

    while attempts < max_attempts:
        try:
            guess = int(input(f"시도 {attempts + 1}/{max_attempts} - 숫자를 입력하세요: "))
        except ValueError:
            print("잘못된 입력입니다. 숫자를 입력해주세요.")
            continue

        attempts += 1

        if guess < secret_number:
            print("너무 작습니다!")
        elif guess > secret_number:
            print("너무 큽니다!")
        else:
            print(f"축하합니다! {attempts}번 만에 숫자를 맞추셨습니다. 정답은 {secret_number}입니다.")
            return

    print(f"아쉽네요. 정답은 {secret_number}였습니다. 다음 기회에!")

def main():
    """게임 시작 및 재시작 로직"""
    while True:
        play_guessing_game()
        play_again = input("다시 플레이하시겠습니까? (yes/no): ").lower()
        if play_again != 'yes':
            print("게임을 종료합니다. 즐거웠습니다!")
            break

if __name__ == "__main__":
    main()
