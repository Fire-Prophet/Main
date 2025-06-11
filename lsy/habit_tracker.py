import datetime

habit = input("추적할 습관을 입력하세요 (예: 물 마시기): ")
date = datetime.date.today()

with open("habits.txt", "a", encoding="utf-8") as f:
    f.write(f"{date}: {habit}\n")

print(f"✅ {date}에 '{habit}' 습관이 기록되었습니다!")
