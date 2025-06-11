class Question:
    def __init__(self, text, option_a, option_b, score_a, score_b):
        self.text = text
        self.option_a = option_a
        self.option_b = option_b
        self.score_a = score_a
        self.score_b = score_b

    def ask(self):
        while True:
            print(f"\n🧠 질문: {self.text}")
            print(f"A. {self.option_a}")
            print(f"B. {self.option_b}")
            answer = input("👉 선택하세요 (A/B): ").strip().upper()

            if answer == 'A':
                return self.score_a
            elif answer == 'B':
                return self.score_b
            else:
                print("❗ 잘못된 입력입니다. A 또는 B만 입력하세요.")
