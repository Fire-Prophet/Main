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

    # 면적 기준 덧셈 (면적 합)
    def __add__(self, other):
        return self.area() + other.area()

    # 면적 기준 뺄셈 (면적 차)
    def __sub__(self, other):
        return self.area() - other.area()

    # 면적 기준 비교
    def __eq__(self, other):
        return self.area() == other.area()

    def __ge__(self, other):
        return self.area() >= other.area()

    # 너비 기준 비교
    def __le__(self, other):
        return self._width <= other._width


# 테스트 코드
if __name__ == "__main__":
    r1 = Rectangle(4, 5)
    r2 = Rectangle(3, 3)

    print(r1)
    print(r2)

    print("r1의 면적:", r1.area())
    print("r1의 둘레:", r1.perimeter())

    r1.resize(2)
    print("크기 조정 후 r1:", r1)
    print("크기 조정 후 r1의 면적:", r1.area())
    print("크기 조정 후 r1의 둘레:", r1.perimeter())

    print(f"r1 + r2(면적 합): {r1 + r2}")
    print(f"r1 - r2(면적 차): {r1 - r2}")

    print(f"r1 == r2(면적 비교): {r1 == r2}")
    print(f"r1 >= r2(면적 비교): {r1 >= r2}")
    print(f"r1 <= r2(너비 비교): {r1 <= r2}")
