import random

emojis = ["😀", "😅", "😎", "🤖", "🐱", "🍀", "🍕", "🚀", "🌈", "🎉"]
symbols = "!@#$%^&*"
password = "".join(random.choices(emojis + list(symbols), k=8))

print("🔐 이모지 비밀번호:", password)
