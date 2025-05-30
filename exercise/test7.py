##내용 복습
fav_fruits = input("좋아하는 과일들을 입력하세요 : ").split()

print("입력한 과일 목록 :", " ".join(fav_fruits))
print(f"리스트 길이 : {len(fav_fruits)}")

if "kiwi" not in fav_fruits:
    fav_fruits.insert(1, "kiwi")

if "banana" in fav_fruits:
    fav_fruits.remove("banana")
    print("제거됨")

last_fruit = fav_fruits.pop()
print(f"마지막 과일은 {last_fruit}입니다.")

fav_fruits.sort()
fav_fruits.reverse()
print(f"최종 리스트 : {fav_fruits}")