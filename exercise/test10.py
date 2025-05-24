from item.item import Item

class Player:
    def __init__(self, name):
        self._name = name
        self._hp = 100
        self._max_hp = 100
        self._stamina = 50
        self._luck = 10
        self._currency = 0

        self._items = []  # 가방(인벤토리)

        # ✅ 장착 슬롯 (목걸이 포함)
        self._equipped = {
            "weapon": None,
            "armor": None,
            "accessory": None   # ✅ 목걸이 / 반지 등 장착 가능!
        }

        self._companions = []

    @property
    def hp(self):
        return self._hp

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = max(0, value)

    def take_damage(self, damage: int):
        self._hp -= damage
        if self._hp < 0:
            self._hp = 0

    def die(self):
        print(f"{self._name}이(가) 쓰러졌습니다.")
        # TODO: 리스폰/부활 로직 추가 가능

    def strengthen_stat(self, stat: str, amount: int):
        if stat == "luck":
            self._luck += amount
        elif stat == "stamina":
            self._stamina += amount
        elif stat == "hp":
            self._max_hp += amount

    def add_item(self, item: Item):
        self._items.append(item)

    def get_inventory(self):
        return self._items

    def get_equipped(self):
        return self._equipped

    def equip_item(self, item: Item):
        if item.item_type not in self._equipped:
            print(f"장착 불가: {item.item_type}")
            return False

        # 기존 장착 아이템이 있다면 스탯 회수
        old_item = self._equipped[item.item_type]
        if old_item:
            self.remove_stat_changes(old_item)

        # 새 아이템 장착
        self._equipped[item.item_type] = item
        self.apply_stat_changes(item)
        return True

    def unequip_item(self, item_type: str):
        item = self._equipped.get(item_type)
        if item:
            self.remove_stat_changes(item)
            self._equipped[item_type] = None
            return True
        return False

    def apply_stat_changes(self, item: Item):
        for stat, value in item.stat_changes.items():
            if stat == "hp":
                self._max_hp += value
                self._hp += value
            elif stat == "stamina":
                self._stamina += value
            elif stat == "luck":
                self._luck += value

    def remove_stat_changes(self, item: Item):
        for stat, value in item.stat_changes.items():
            if stat == "hp":
                self._max_hp -= value
                self._hp = min(self._hp, self._max_hp)
            elif stat == "stamina":
                self._stamina -= value
            elif stat == "luck":
                self._luck -= value
