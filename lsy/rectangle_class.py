class Rectangle:
    # 프라이빗 변수: _width, _height
    def __init__(self, width, height):
        self._width = width
        self._height = height

    # 면적 반환
    def area(self):
        return self._width * self._height

    # 둘레 반환
    def perimeter(self):
        return 2 * (self._width + self._height)

    # 크기 조정
    def resize(self, factor):
        self._width *= factor
        self._height *= factor
