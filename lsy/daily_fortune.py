import random

user = input("이름을 입력하세요: ")
fortunes = [
    "오늘은 좋은 일이 생겨요!",
    "조심해야 할 날이에요.",
    "기회가 찾아옵니다!",
    "편한 하루가 될 거예요."
]
print(f"{user}님의 운세: {random.choice(fortunes)}")
