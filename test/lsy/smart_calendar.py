from datetime import datetime

tasks = {
    "2025-06-05": ["회의 준비", "과제 제출"],
    "2025-06-07": ["운동", "친구 만나기"],
}

today = datetime.today().strftime("%Y-%m-%d")
print(f"📅 오늘 날짜: {today}")

if today in tasks:
    print(f"오늘 일정 {len(tasks[today])}개: {', '.join(tasks[today])}")
else:
    print("오늘은 일정이 없습니다.")
