class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def area(self):
        return self._width * self._height

    def perimeter(self):
        return 2 * (self._width + self._height)

    def resize(self, factor):
        self._width *= factor
        self._height *= factor

    def __str__(self):
        return f"Rectangle(width={self._width}, height={self._height})"

    def __add__(self, other):
        return self.area() + other.area()

    def __sub__(self, other):
        return self.area() - other.area()

    def __eq__(self, other):
        return self.area() == other.area()

    def __ge__(self, other):
        return self.area() >= other.area()

    def __le__(self, other):
        return self._width <= other._width

    def __lt__(self, other):
        return self._width < other._width


# r3 : width = 3, height = 3
# r4 : width = 5, height = 7
r3 = Rectangle(3, 3)
r4 = Rectangle(5, 7)

print(r3 <= r4)  # True

if r3 < r4:
    print("r3가 r4보다 너비가 작습니다.")
