import random

class RandomClass1:
    def __init__(self):
        self.value = random.randint(1, 100)

    def get_value(self):
        return self.value

    def set_value(self, new_value):
        self.value = new_value
