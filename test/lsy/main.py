from lsy.color_game_en import ColorGameEN
from color_game_kr import ColorGameKR

def main():
    print("컬러 맞추기 게임에 오신 것을 환영합니다!")
    print("1. 한글 → 영어")
    print("2. 영어 → 한글")

    choice = input("모드를 선택하세요 (1 또는 2): ").strip()

    if choice == '1':
        print("\n[한글 → 영어 모드 시작]\n")
        game = ColorGameEN()
        game.play()
    elif choice == '2':
        print("\n[영어 → 한글 모드 시작]\n")
        game = ColorGameKR()
        game.play()
    else:
        print("잘못된 선택입니다. 프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
