from datetime import datetime

hour = datetime.now().hour
if hour < 12:
    print("좋은 아침이에요 ☀️")
elif hour < 18:
    print("좋은 오후에요 🌤")
else:
    print("좋은 저녁이에요 🌙")
