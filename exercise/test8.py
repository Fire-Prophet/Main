# 튜플
fruits = ("apple", "banana", "cherry")

t = (1, 2, 3)

x = (5, )
y = (5)

t = ("a", "b", "c", "d")
print(t[0])
print(t[1:3])


# 문제1
colors = ("red", "green", "blue", "yellow")

print(colors[1], colors[3])


# 문제2
sum = 0
num = tuple(map(int, input("숫자 3개를 입력하세요 : ").split()))

for i in range(3):
    sum += num[i]

print(sum)