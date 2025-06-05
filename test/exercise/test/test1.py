#Day1 print
name = "bjw1055"
age = 24
food = "fried chicken"

print(name, "님은 ", age, "살이고, ", "좋아하는 음식은 ", food, "입니다.")



#Day2 input, map, split
age = input("나이를 입력하세요:")
age = int(age)
print(f"내년 나이는 {age+1}세 입니다.")


name = input("이름을 입력하세요:")
age = input("나이를 입력하세요:")
fav_num = input("좋아하는 숫자를 입력하세요:")

print(f"이름은 {name}, 나이는 {age}, 좋아하는 숫자는 {fav_num},입니다.")
print(f"좋아하는 숫자를 2배한 값은 {int(fav_num)*2}이고, 3배한 값은 {int(fav_num)*3}입니다.")


text = "hello world python"
word = text.split()
print(word)
print(type(word))


# #예제1
#  a, b = map(int, input("숫자 두개를 입력하세요:").split())

#  print(f"두 수의 합은 {a + b}이다.")


# #예제2
# a, b, c = map(float, input("실수 세개를 입력하세요:").split())
# print(f"평균은 {((a + b + c)/3):.1f}입니다.")


# #예제3
#  text = input()
#  word = text.split()
#  print(word)



#Day3 조건문 if
#예제1
age = int(input("나이를 입력하세요:"))
if(age >= 20):
    print("성인입니다.")
else:
    print("미성년자입니다.")


#예제2
a, b = map(int, input("숫자 두개를 입력하세요:").split())

if(a > b):
    print("첫 번째 숫자가 더 큽니다.")
elif(a == b):
    print("두 수의 크기가 같습니다.")
else:
    print("두 번째 숫자가 더 큽니다.")


#예제3
score = int(input("시험점수를 입력하세요:"))

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
