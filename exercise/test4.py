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


##Day5까지 복습예제제
name = input("사용자 이름을 입력하세요 : ")
age = int(input("사용자 나이를 입력하세요 : "))
interest = input("사용자 관심사를 입력하세요 : ")
grade = list(map(float, input("사용자 평점을 입력하세요 : ").split()))

if age >= 20:
    print("성인입니다.")
else:
    print("미성년자입니다.")

print(f"관심 분야 : {interest}")

sum = 0
for i in grade:
    sum += i
avg = sum / len(grade)

if avg >= 4.0:
    print("평가 : 매우 만족")
elif avg >= 3.0:
    print("평가 : 보통")
else:
    print("평가 : 개선 필요")


# Day6 break, continue 보여준 예제
while True:
    word = input("단어 입력 (exit 입력 시 종료) : ")
    if word == "exit":
        break
    print(f"입력한 단어 : {word}")


for i in range(1, 6):
    if i == 3:
        continue
    print(i)


#실습1
sum = 0
while True:
    num = int(input("수를 입력하세요 : "))
    if num < 0:
        print("음수는 입력할 수 없습니다.")
        continue
    elif num == 0:
        break
    else:
        sum += num
print(sum)

#실습2
for i in range(1, 101):
    print(i)
    if i == 42:
        print("42에서 멈춥니다.")
        break
