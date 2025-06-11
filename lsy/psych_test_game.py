from question import Question

class TestGame:
    def __init__(self, user_name):
        self.user_name = user_name
        self.questions = [
            Question("친구와 약속을 잡을 때 나는?", "내가 먼저 연락한다", "상대가 연락해오길 기다린다", 1, 0),
            Question("주말에 나는?", "사람들과 어울리는 걸 좋아한다", "혼자 있는 시간이 필요하다", 1, 0),
            Question("낯선 사람과의 대화는?", "재미있고 흥미롭다", "불편하고 피하고 싶다", 1, 0),
            Question("여행 스타일은?", "즉흥적인 게 좋다", "계획적인 게 좋다", 1, 0),
            Question("갈등 상황에서 나는?", "직접 해결하려 한다", "피하고 조용히 넘긴다", 1, 0)
        ]
        self.score = 0

    def run(self):
        print(f"\n👤 {self.user_name}님의 심리 테스트를 시작합니다!")
        for q in self.questions:
            self.score += q.ask()

        self.show_result()

    def show_result(self):
        print("\n📝 테스트 결과:")
        if self.score >= 4:
            print("✅ 외향적이고 활발한 성격이에요!")
        elif self.score >= 2:
            print("😌 상황에 따라 유연한 성격이에요.")
        else:
            print("🤫 조용하고 내향적인 성격이에요.")
