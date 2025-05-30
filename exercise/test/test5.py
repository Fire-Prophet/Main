# list 학습
fruits = ["apple", "banana", "cherry"]
print(fruits[0])
print(fruits[-1])
print(fruits[0:2])


fruits = ["apple", "banana", "cherry"]
fruits.append("melon")
fruits.insert(0, "kiwi")
fruits.remove("apple")
last = fruits.pop()
print(fruits)
print(last)

num = [5,3,23,42,15,46,45,745,65,12435,123]
print(num)
num.sort()
print(num)
num.reverse()
print(num)
print(len(num))


#실습문제1
fruits = ["apple", "banana", "cherry"]

for i in fruits:
    print(i)


#list 조작 연습 append
fruits =[]

fruits.append("apple")
fruits.append("banana")
fruits.append("cherry")
print(fruits)

#insert
fruits.insert(1, "kiwi")
print(fruits)

#remove
fruits.remove("banana")
print(fruits)

#sort
fruits.sort()
print(fruits)

#reverse, len
fruits.reverse()
print(fruits, len(fruits))


#pop 실습문제 (위랑 따로)
animals = ["dog", "cat", "rabbit"]
last_animals = animals.pop()
print(f"꺼낸 동물 : {last_animals}")
print(f"남은 리스트 : {animals}")

#pop 실습문제 2
nums = [10, 20, 30, 40, 50]
nums_pop = nums.pop(2)
print(f"꺼낸 값 : {nums_pop}")
print(f"변경된 리스트 : {nums}")


#pop 오류메시지 문제
empty_list = []
empty_list.pop()
print(empty_list)