import time
import random

sentence = "The quick brown fox jumps over the lazy dog."
print("다음 문장을 최대한 빠르게 입력하세요:")
print(sentence)

input("준비되면 Enter를 누르세요...")
start = time.time()
typed = input("> ")
end = time.time()

if typed.strip() == sentence:
    speed = len(sentence) / (end - start)
    print(f"⌨️ 속도: {speed:.2f} 문자/초")
else:
    print("❌ 문장이 일치하지 않아요.")
