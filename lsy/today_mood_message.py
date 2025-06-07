# today_mood_message.py
import random
from datetime import date

# 오늘 날짜
today = date.today()
print(f"📅 오늘은 {today}입니다.\n")

# 기분 리스트와 추천 메시지
mood_messages = {
    "😊 행복": "오늘도 활짝 웃는 하루가 되길 바라요!",
    "😐 평범": "가끔은 평범함이 가장 편안하죠. 오늘도 무탈하게 보내요.",
    "😴 피곤": "휴식이 필요해 보여요. 틈틈이 쉬어가요!",
    "😡 짜증": "잠깐 숨 고르고, 좋아하는 걸 해봐요. 기분이 좀 나아질 거예요.",
    "🥳 신남": "이 에너지 그대로! 멋진 하루가 될 거예요!"
}

# 랜덤으로 오늘의 기분 선택
mood, message = random.choice(list(mood_messages.items()))

# 출력
print(f"🧠 오늘의 기분: {mood}")
print(f"💬 추천 메시지: {message}")
