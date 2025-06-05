class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

v1 = Vector2D(30, 40)
v2 = Vector2D(10, 20)

v3 = v1 + v2
print('v1 + v2 =', v3)
