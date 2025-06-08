from test_game import TestGame

if __name__ == "__main__":
    while True:
        name = input("🧑 이름을 입력하세요: ").strip()
        if name:
            break
        else:
            print("⚠️ 이름은 비워둘 수 없습니다. 다시 입력해주세요.")
    
    game = TestGame(name)
    game.run()
