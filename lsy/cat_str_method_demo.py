class Cat:
    def __init__(self, name, color):
        self.name = name
        self.color = color

    def __str__(self):
        return f'Cat(name = {self.name}, color = {self.color})'

# 인스턴스 생성
nabi = Cat('나비', '검은색')
nero = Cat('네로', '흰색')

# 출력
print(nabi)
print(nero)