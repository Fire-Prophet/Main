import random
from dungeon_player import Player

def josa(word, josa_pair):
    return josa_pair[0] if has_final(word[-1]) else josa_pair[1]

def has_final(char):
    return (ord(char) - 44032) % 28 != 0

class DungeonGame:
    def __init__(self, player, max_turns):
        self.player = player
        self.visited = 0
        self.max_turns = max_turns
        self.next_rooms = {}
        self.monsters = [
            {"name": "고블린", "damage": (10, 20), "gold": 10},
            {"name": "해골 병사", "damage": (15, 25), "gold": 15},
            {"name": "오우거", "damage": (20, 30), "gold": 20},
            {"name": "슬라임", "damage": (5, 15), "gold": 5},
            {"name": "도적", "damage": (10, 20), "gold": 10, "steals": True},
            {"name": "미니 드래곤", "damage": (25, 40), "gold": 30}
        ]

    def play(self):
        print(f"\n🧙‍♂️ {self.player.name}님의 던전 모험이 시작됩니다!\n")
        print(f"🔄 남은 턴 수: {self.max_turns - self.visited}\n")
        while self.player.hp > 0 and self.visited < self.max_turns:
            self.generate_next_rooms()
            self.ask_use_item()
            direction = self.choose_direction()
            self.enter_room(direction)
            print(f"🔄 남은 턴 수: {self.max_turns - self.visited - 1}\n")
            self.visited += 1
        self.ending()

    def generate_next_rooms(self):
        options = ["몬스터", "보물 상자", "회복약", "빈 방", "막힌 길"]
        directions = ['left', 'right', 'center']
        self.next_rooms = {d: random.choice(options) for d in directions}
        if all(room == "막힌 길" for room in self.next_rooms.values()):
            chosen = random.choice(directions)
            self.next_rooms[chosen] = random.choice(["몬스터", "보물 상자", "회복약", "빈 방"])

    def ask_use_item(self):
        if not self.player.inventory:
            return
        while True:
            choice = input(f"🎒 {self.player.name}님의 인벤토리: {self.player.inventory}\n아이템을 사용하시겠습니까? (y/n): ").strip().lower()
            if choice == 'y':
                item = input("사용할 아이템 이름을 입력하세요: ").strip()
                if item == "지도 조각":
                    self.reveal_next_rooms()
                self.player.use_item(item)
                break
            elif choice == 'n':
                break
            else:
                print("❗ y 또는 n만 입력해주세요.")

    def reveal_next_rooms(self):
        print("🗺️ 지도 조각 발동! 다음 방의 정보입니다:")
        for direction, room in self.next_rooms.items():
            print(f" - {direction.upper()} 방향: [{room}]")

    def choose_direction(self):
        print("🧭 이동할 수 있는 방향: 왼쪽(left), 가운데(center), 오른쪽(right)")
        mapping = {'왼쪽': 'left', '가운데': 'center', '오른쪽': 'right',
                   'left': 'left', 'center': 'center', 'right': 'right'}
        while True:
            direction_input = input("➡️ 어느 방향으로 이동하시겠습니까? ").strip().lower()
            direction = mapping.get(direction_input)
            if not direction:
                print("❗ 방향은 왼쪽, 가운데, 오른쪽 중 하나로 입력해주세요.")
                continue
            if self.next_rooms.get(direction) == "막힌 길":
                print(f"🚧 {direction.upper()} 방향은 막힌 길입니다! 다른 길을 선택하세요.")
                continue
            return direction

    def enter_room(self, direction):
        print(f"\n➡️ {self.player.name}님이 {direction.upper()} 방향으로 이동합니다...")
        room = self.next_rooms[direction]
        print(f"🚪 방에 들어갑니다... [{room}]")
        self.resolve_room(room)

    def resolve_room(self, room):
        if room == "함정":
            self.player.take_damage(random.randint(10, 30))
        elif room == "회복약":
            while True:
                try:
                    choice = input(f"💊 {self.player.name}님, 회복약을 사용하시겠습니까? (y/n): ").strip().lower()
                    if choice not in ['y', 'n']:
                        raise ValueError("y 또는 n만 입력해주세요.")
                    break
                except ValueError as e:
                    print("❗ 입력 오류:", e)
            if choice == 'y':
                self.player.heal(random.randint(10, 25))
            else:
                print("😐 회복약을 사용하지 않았습니다.")
        elif room == "몬스터":
            self.handle_monster()
        elif room == "보물 상자":
            item = random.choice(["회복약", "폭탄", "황금 열쇠", "마법 부적", "도끼", "지도 조각"])
            self.player.add_item(item)
            gold = random.randint(5, 20)
            self.player.earn_gold(gold)
        else:
            print("😶 아무 일도 일어나지 않았습니다.")

    def handle_monster(self):
        monster = random.choice(self.monsters)
        print(f"👹 {monster['name']}이(가) 나타났습니다! {self.player.name}님, 준비하세요!")

        if self.player.has_talisman:
            print(f"✨ 마법 부적의 힘으로 {monster['name']}(을)를 자동으로 처치했습니다!")
            self.player.has_talisman = False
            self.player.earn_gold(monster.get("gold", 0))
            self.player.add_item("몬스터의 송곳니")
            return

        while True:
            try:
                fight = input("⚔️ 싸우시겠습니까? (y/n): ").strip().lower()
                if fight not in ['y', 'n']:
                    raise ValueError("y 또는 n만 입력해주세요.")
                break
            except ValueError as e:
                print("❗ 입력 오류:", e)

        if fight == 'y':
            win = random.choices([True, False], weights=[60, 40])[0]
            if "도끼" in self.player.inventory:
                win = random.choices([True, False], weights=[80, 20])[0]
            if win:
                print(f"🎉 {self.player.name}님이 {monster['name']}(을)를 처치했습니다!")
                self.player.earn_gold(monster.get("gold", 0))
                self.player.add_item("몬스터의 송곳니")
            else:
                self.player.take_damage(random.randint(*monster["damage"]))
                if monster.get("steals"):
                    steal = min(10, self.player.gold)
                    self.player.gold -= steal
                    print(f"💰 도적이 {steal} 골드를 훔쳐 달아났습니다!")
        else:
            print(f"🏃‍♂️ {self.player.name}님이 도망쳤습니다!")

    def ending(self):
        print(f"\n🏁 {self.player.name}님의 던전 탐험 종료!")
        print(f"❤️ 최종 체력: {self.player.hp}")
        print(f"🎒 최종 인벤토리: {self.player.inventory}")
        print(f"💰 총 골드: {self.player.gold}")
        if "황금 열쇠" in self.player.inventory:
            print(f"🔓 {self.player.name}{josa(self.player.name, '은는')} 황금 열쇠를 사용하여 무사히 탈출했습니다!")
        else:
            print(f"🚪 {self.player.name}{josa(self.player.name, '은는')} 열쇠가 없어 출구를 찾지 못했습니다... 탈출 실패!")
