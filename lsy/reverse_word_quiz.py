import random

words = ['파이썬', '코딩', '데이터', '인공지능', '프로그래밍']
quiz = random.choice(words)
print("이 단어를 거꾸로 적어보세요:", quiz[::-1])
answer = input("당신의 답: ")
print("정답입니다!" if answer == quiz else "틀렸어요.")
