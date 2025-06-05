import random

class ColorGameEN:
    def __init__(self):  # ✅ 올바른 생성자
        self.color_dict = {  # ✅ 변수 이름 수정
            '빨강': 'red',
            '파랑': 'blue',
            '초록': 'green',
            '노랑': 'yellow',
            '주황': 'orange',
            '보라': 'purple',
            '하양': 'white',
            '검정': 'black',
            '회색': 'gray',
            '주홍색': 'scarlet',
            '남색': 'navy',
            '청록색': 'turquoise'
        }
        self.num_questions = 5
        self.score = 0

    def play(self):  # ✅ 클래스 밖으로 들여쓰기 수정
        print("한글 색깔 이름을 보고 영어로 맞춰보세요!")
        print("예시: 빨강 -> red")
        print("게임 중 '#'을 입력하면 종료됩니다.")
        print(f"\n총 {self.num_questions}문제가 출제됩니다.\n")

        questions = random.sample(list(self.color_dict.keys()), k=self.num_questions)

        for idx, color_kr in enumerate(questions, 1):
            print(f"{idx}번째 문제: {color_kr}")
            guess = input("영어로 입력하세요: ").strip().lower()

            if guess == '#':
                print("게임을 중단했습니다.")
                break
            elif guess == self.color_dict[color_kr]:
                print("**정답입니다!**\n")
                self.score += 1
            else:
                print(f"틀렸어요! ㅠㅠ 정답은 '{self.color_dict[color_kr]}'입니다.\n")

        print("게임 종료!")
        print(f"정답 수: {self.score} / {self.num_questions}")
        print(f"정답률: {round((self.score / self.num_questions) * 100)}%")
