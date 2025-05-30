## Day 5 while 문 예제
#문제1
i = 1
while i <= 10:
    print(i)
    i += 1

#문제2
i = int(input("입력 : "))
sum = 0
while i != 0:
    sum += i
    i = int(input("입력 : "))
print(sum)