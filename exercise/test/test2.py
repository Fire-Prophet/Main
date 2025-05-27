# #Day4 반복문
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)

for i in range(1, 11):
     print(i)

count = 0
while count < 5:
    print(count)
    count += 1

fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)

for ch in "hello":
    print(ch)

#for문 예제1
for i in range(1,11):
    print(i)


#예제2
count = 0
for i in range(1, 11):
    count += i
print(f"합계는 {count}입니다.")


#예제3
n = int(input("정수를 입력하세요:"))

for i in range(n+1):
    if(i % 2 != 0):
        print(i)


#예제4
a = input("문자열을 입력하세요:")

for i in a:
    print(i)



#Day5 while문 예제1
i = 1
while i < 11:
    print(i)
    i += 1


#예제2
a = int(input("입력:"))
sum = 0
while a != 0:
    sum += a
    a = int(input("입력:"))
print(f"합계: {sum}")



#Day6 break & continue
while True:
    word = input("단어를 입력하세요 (종료하려면 exit):")
    if word == "exit":
        break
    print(f"입력한 단어: {word}")


for i in range(1, 6):
    if i == 3:
        continue
    print(i)


#예제1
sum = 0
while True:
    num = int(input("입력: "))
    if num < 0:
        print("음수는 입력할 수 없습니다.")
        continue
    elif num == 0:
        break
    sum += num
print(f"출력: 합계는 {sum}입니다.")


#예제2
for i in range(1, 101):
    if(i == 42):
        print(f"{i}에서 멈춥니다.")
        break
    print(i)
