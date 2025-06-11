class Character:
    def __init__(self, name, wears_glasses, left_handed):
        self.name = name
        self.wears_glasses = wears_glasses
        self.left_handed = left_handed

    def __str__(self):
        return f"{self.name} (안경: {'O' if self.wears_glasses else 'X'}, 왼손잡이: {'O' if self.left_handed else 'X'})"
