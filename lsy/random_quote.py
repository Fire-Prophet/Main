import random

quotes = [
    "성공은 준비와 기회의 만남이다.",
    "실패는 성공으로 가는 또 다른 길일 뿐이다.",
    "어제보다 나은 오늘을 만들어라.",
    "노력은 배신하지 않는다.",
    "작은 습관이 큰 변화를 만든다.",
    "포기하지 마라, 끝까지 가보자.",
    "시간은 금이다, 낭비하지 마라."
]

def print_random_quote():
    quote = random.choice(quotes)
    print(f"\n💬 오늘의 격언:\n\"{quote}\"\n")

if __name__ == "__main__":
    print_random_quote()
