positive = ['좋아', '행복', '기뻐', '사랑']
negative = ['싫어', '짜증', '화나', '슬퍼']

text = input("문장 입력: ")
if any(word in text for word in positive):
    print("이 문장은 긍정적인 느낌이에요!")
elif any(word in text for word in negative):
    print("이 문장은 부정적인 느낌이에요!")
else:
    print("중립적인 문장이네요.")
