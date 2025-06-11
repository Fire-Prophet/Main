from dungeon_player import Player
from dungeon_map import DungeonGame

def get_turn_count():
    while True:
        try:
            turns = int(input("🎯 탐험할 턴 수를 입력하세요 (최소 3, 최대 10): "))
            if 3 <= turns <= 10:
                return turns
            else:
                print("⚠️ 범위는 3~10 사이여야 합니다.")
        except ValueError:
            print("❗ 숫자만 입력해주세요.")

if __name__ == "__main__":
    while True:
        name = input("🧑 이름을 입력하세요: ").strip()
        if name:
            break
        else:
            print("⚠️ 이름은 공백일 수 없습니다. 다시 입력해주세요.")
    
    player = Player(name)
    turns = get_turn_count()
    game = DungeonGame(player, turns)
    game.play()
