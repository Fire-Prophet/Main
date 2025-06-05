class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        print("멍멍~~!!")

# 인스턴스 생성
my_dog = Dog('jindo')

# 메서드 호출
my_dog.bark()