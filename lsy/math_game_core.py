from problem import MathProblem

class MathQuizGame:
    def __init__(self, user_name):
        self.user_name = user_name
        self.total_questions = 5
        self.score = 0

    def start(self):
        print(f"\n🧮 {self.user_name}님의 수학 퀴즈를 시작합니다!\n")

        for i in range(1, self.total_questions + 1):
            print(f"📘 문제 {i}:")
            problem = MathProblem()
            print(problem.display())
            user_input = input("👉 정답을 입력하세요: ")

            if problem.check_answer(user_input):
                print("✅ 정답입니다!\n")
                self.score += 1
            else:
                print(f"❌ 오답입니다. 정답은 {problem.answer}입니다.\n")

        self.show_result()

    def show_result(self):
        print(f"🎯 최종 점수: {self.score} / {self.total_questions}")
        if self.score == self.total_questions:
            print("🎉 수학 천재네요!")
        elif self.score >= 3:
            print("😊 잘했어요!")
        else:
            print("📖 조금 더 연습해볼까요?")
