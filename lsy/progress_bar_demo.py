import time
for i in range(1, 11):
    print(f"\r진행중: [{'#' * i}{'.' * (10 - i)}] {i*10}%", end="")
    time.sleep(0.2)
print("\n완료!")
