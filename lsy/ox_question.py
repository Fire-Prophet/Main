class Question:
    def __init__(self, text, answer):  # answer는 'O' 또는 'X'
        self.text = text
        self.answer = answer.upper()

    def ask(self):
        while True:
            print(f"\n❓ 문제: {self.text}")
            user_answer = input("👉 O 또는 X를 입력하세요: ").strip().upper()
            if user_answer in ['O', 'X']:
                return user_answer == self.answer
            else:
                print("❗ 잘못된 입력입니다. O 또는 X만 입력하세요.")
