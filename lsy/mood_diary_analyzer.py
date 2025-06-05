positive = ["좋아", "행복", "기분 좋아", "신나"]
negative = ["싫어", "우울", "짜증", "화나"]

text = input("오늘 기분을 간단히 표현해보세요: ")

pos = any(word in text for word in positive)
neg = any(word in text for word in negative)

if pos and not neg:
    print("오늘은 좋은 하루네요 😊")
elif neg and not pos:
    print("오늘은 좀 힘들었군요 😥")
elif pos and neg:
    print("복잡한 하루였군요 😐")
else:
    print("기분이 잘 느껴지지 않아요 😶")
