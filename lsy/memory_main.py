from memory_core import MemoryGame

def main():
    user_name = input("🧑 이름을 입력하세요: ").strip()

    print("\n🎮 난이도를 선택하세요:")
    print("1. 쉬움 (시작 개수 작고 시간 여유 있음)")
    print("2. 보통")
    print("3. 어려움 (더 많은 항목, 짧은 시간)")
    difficulty = input("> 선택: ")

    print("\n🧠 기억할 항목을 선택하세요:")
    print("1. 숫자")
    print("2. 한글 단어 (또는 '한글')")
    print("3. 색상")
    print("4. 영어 단어 (또는 '영어')")
    category_input = input("> 선택: ").strip()

    category_dict = {
        "1": "1", "숫자": "1",
        "2": "2", "한글": "2", "한글 단어": "2",
        "3": "3", "색상": "3",
        "4": "4", "영어": "4", "영어 단어": "4"
    }
    category = category_dict.get(category_input, "1")

    game = MemoryGame(user_name, difficulty, category)
    game.start()

if __name__ == "__main__":
    main()

