from ox_question import Question

class QuizGame:
    def __init__(self, user_name):
        self.user_name = user_name
        self.questions = [
            Question("사과는 과일이다. (O/X)", "O"),
            Question("대한민국의 수도는 부산이다. (O/X)", "X"),
            Question("2 + 2는 5이다. (O/X)", "X"),
            Question("지구는 태양 주위를 돈다. (O/X)", "O"),
            Question("물은 불보다 뜨겁다. (O/X)", "X"),
        ]
        self.score = 0

    def start(self):
        print(f"\n📚 {self.user_name}님의 OX 퀴즈를 시작합니다!\n")
        for q in self.questions:
            if q.ask():
                print("✅ 정답입니다!")
                self.score += 1
            else:
                print("❌ 오답입니다.")

        self.show_result()

    def show_result(self):
        print(f"\n🎯 총 점수: {self.score} / {len(self.questions)}")
        if self.score == len(self.questions):
            print("🎉 완벽해요! 축하합니다!")
        elif self.score >= 3:
            print("😊 꽤 잘했어요!")
        else:
            print("😢 조금 더 공부가 필요해요.")
