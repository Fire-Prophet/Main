class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.inventory = []
        self.gold = 0
        self.has_talisman = False

    def take_damage(self, amount):
        self.hp -= amount
        print(f"💥 {self.name}님이 {amount}의 피해를 입었습니다! 현재 HP: {self.hp}")
        if self.hp <= 0:
            print(f"☠️ {self.name}님의 체력이 0이 되어 쓰러졌습니다... 게임 오버!")

    def heal(self, amount):
        self.hp += amount
        print(f"💊 {self.name}님의 체력을 {amount} 회복했습니다! 현재 HP: {self.hp}")

    def add_item(self, item):
        self.inventory.append(item)
        print(f"🎁 {self.name}님이 {item}을(를) 얻었습니다! 인벤토리: {self.inventory}")

    def use_item(self, item):
        if item not in self.inventory:
            print(f"❌ '{item}' 아이템이 인벤토리에 없습니다.")
            return
        if item == "회복약":
            self.heal(30)
        elif item == "폭탄":
            print("💣 폭탄을 던졌습니다! (다음 전투에서 자동 승리 처리)")
        elif item == "황금 열쇠":
            print("🔑 황금 열쇠는 마지막 탈출에 사용됩니다.")
            return
        elif item == "마법 부적":
            self.has_talisman = True
            print("✨ 마법 부적을 사용했습니다! 다음 전투에서 무조건 승리합니다.")
        elif item == "도끼":
            print("🪓 도끼를 장비했습니다. 몬스터를 쉽게 이길 수 있습니다!")
        elif item == "지도 조각":
            print("🗺️ 지도 조각을 사용했습니다! (다음 방 정보 확인은 자동 처리됨)")
        else:
            print("❔ 알 수 없는 아이템입니다.")
        self.inventory.remove(item)

    def earn_gold(self, amount):
        self.gold += amount
        print(f"🪙 {self.name}님이 골드를 {amount} 얻었습니다! 현재 총 골드: {self.gold}")
