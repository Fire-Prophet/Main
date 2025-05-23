# Day 1 복습
name = "반준우"
age = 0
fav_food = "chicken"

print(f"{name}님은 {age}살이고 좋아하는 음식은 {fav_food}입니다.")



# Day 2 복습
name = input("이름을 입력하세요 : ")
age = input("나이를 입력하세요 : ")
fav_num = int(input("좋아하는 숫자를 입력하세요 : "))

print(f"{name}님은 {age}살이고, 좋아하는 숫자의 두 배는 {fav_num * 2}입니다.")



# Day 2 map, split 복습
a, b = map(int, input("두 숫자를 입력하세요 : ").split())
print(a + b)

# map, split 복습 2
name, age, fav_food = map(str, input("이름과 나이와 좋아하는 음식을 입력하세요 : ").split())
print(f"{name}님은 {age}살이고 좋아하는 음식은 {fav_food}입니다.")




# Day3 if 반복문 복습
score = int(input("점수를 입력하세요 : "))

if(score >= 90):
    print("A")
elif(score >= 80):
    print("B")
elif(score >= 70):
    print("C")
elif(score >= 60):
    print("D")
else:
    print("F")


# for 반복문 복습
for i in range(10):
    print(i+1)


## for 반복문 더 요청한 예제 1
sum = 0
for i in range(1, 101):
    sum += i
print(sum)


## 예제2
num = int(input("숫자를 입력하세요 : "))
for i in range(1, num + 1):
    if(i % 2 == 0):
        print(i)


## 예제3
list_word = ""
word = input("단어를 입력하세요 : ")
for i in word:
    list_word = list_word + i + "-"
print(list_word)


## 예제4
mul = 0
num = int(input("숫자를 입력하세요 : "))
for i in range(1, 10):
    mul = num * i
    print(f"{num} x {i} = {mul}")
