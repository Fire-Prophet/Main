from character import Character
import random

class MysteryGame:
    def __init__(self):
        self.characters = [
            Character("민수", True, False),
            Character("지혜", False, True),
            Character("철수", True, True),
            Character("유리", False, False)
        ]
        self.criminal = random.choice(self.characters)

    def show_hints(self):
        print("📌 [힌트]")
        print(f"- 범인은 {'안경을 썼어요' if self.criminal.wears_glasses else '안경을 쓰지 않았어요'}.")
        print(f"- 범인은 {'왼손잡이에요' if self.criminal.left_handed else '오른손잡이에요'}.")

    def guess_criminal(self):
        self.show_hints()
        print("\n용의자 목록:")
        for c in self.characters:
            print("-", c)  # 이름 + 특성 출력

        try:
            name = input("\n👮‍♂️ 범인은 누구일까요? 이름을 입력하세요: ")
            found = next((c for c in self.characters if c.name == name), None)

            if not found:
                raise ValueError("존재하지 않는 용의자입니다.")

            if found == self.criminal:
                print("🎉 정답입니다! 범인을 잡았습니다!")
            else:
                print(f"❌ 아쉽네요! 범인은 {self.criminal.name}이었습니다.")
        except ValueError as e:
            print("⚠️ 입력 오류:", e)
