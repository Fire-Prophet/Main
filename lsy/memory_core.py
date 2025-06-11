import time
from memory_sequence import Sequence
import os

class MemoryGame:
    def __init__(self, user_name, difficulty, category):
        self.user_name = user_name
        self.difficulty = difficulty
        self.category = category
        self.correct = 0
        self.lengths = []
        self.set_parameters()

    def set_parameters(self):
        if self.difficulty == "1":
            self.display_time = 5
            self.start_length = 2
        elif self.difficulty == "2":
            self.display_time = 3
            self.start_length = 3 if self.category == "1" else 2
        else:
            self.display_time = 1.5
            self.start_length = 4 if self.category == "1" else 3

    def get_record_filename(self):
        return f"record_{self.user_name}.txt"

    def get_result_filename(self):
        return f"result_{self.user_name}.txt"

    def load_high_score(self):
        try:
            filename = self.get_record_filename()
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def save_high_score(self, score):
        filename = self.get_record_filename()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(str(score))

    def save_result_to_file(self, prev_score):
        filename = self.get_result_filename()
        avg_len = sum(self.lengths) / len(self.lengths) if self.lengths else 0
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"👤 사용자: {self.user_name}\n")
            f.write(f"🎯 맞힌 라운드 수: {self.correct}\n")
            f.write(f"📊 평균 기억 길이: {avg_len:.2f}\n")
            f.write(f"🏅 이전 최고 기록: {prev_score} 라운드\n")
            if self.correct >= 10:
                f.write("🎉 대단해요! 완벽한 기억력!\n")
            elif self.correct >= 5:
                f.write("👏 꽤 괜찮은 기억력이에요!\n")
            else:
                f.write("🧩 조금 더 연습해볼까요?\n")

    def start(self):
        print(f"\n🧠 {self.user_name}님의 기억력 테스트를 시작합니다!\n")

        round_num = 1
        while True:
            print(f"\n📍 ROUND {round_num}")
            length = self.start_length + round_num - 1

            seq = Sequence(length=length, category=self.category)
            self.lengths.append(len(seq.sequence))
            seq.show()

            time.sleep(self.display_time)
            print("\n" * 30)

            user_input = input("🔁 기억나는 항목을 입력하세요: ")
            if seq.check(user_input):
                print("✅ 정답입니다!")
                self.correct += 1
                round_num += 1
            else:
                print(f"❌ 틀렸어요! 정답: {' '.join(str(n) for n in seq.sequence)}")
                break

        self.show_result()

        answer = input("💾 기록을 저장하시겠습니까? (y/n): ").strip().lower()
        prev_score = self.load_high_score()
        if answer == "y":
            self.save_high_score(self.correct)
            print(f"📁 기록이 저장되었습니다. (이번 기록: {self.correct} 라운드)")
        else:
            print("📁 기록이 저장되지 않았습니다.")

        self.save_result_to_file(prev_score)

    def show_result(self):
        print(f"\n👤 사용자: {self.user_name}")
        print(f"🎯 맞힌 라운드 수: {self.correct}")
        avg_len = sum(self.lengths) / len(self.lengths) if self.lengths else 0
        print(f"📊 평균 기억 길이: {avg_len:.2f}")

        prev_score = self.load_high_score()
        print(f"🏅 이전 최고 기록: {prev_score} 라운드")

        if self.correct >= 10:
            print("🎉 대단해요! 완벽한 기억력!")
        elif self.correct >= 5:
            print("👏 꽤 괜찮은 기억력이에요!")
        else:
            print("🧩 조금 더 연습해볼까요?")
