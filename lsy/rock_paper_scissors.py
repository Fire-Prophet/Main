import random

choices = ['가위', '바위', '보']
user = input("가위, 바위, 보 중 선택: ")
comp = random.choice(choices)

print(f"컴퓨터: {comp}")
if user == comp:
    print("무승부!")
elif (user == '가위' and comp == '보') or \
     (user == '바위' and comp == '가위') or \
     (user == '보' and comp == '바위'):
    print("이겼습니다!")
else:
    print("졌습니다!")
