class Dog:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'Dog(name = {self.name})'

# 인스턴스 생성
my_dog = Dog('Jindo')

# 출력
print('my_dog의 정보 :', my_dog)