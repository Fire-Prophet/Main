import time
import sys

text = "나는 유령이다... 👻"

for char in text:
    print(char, end='', flush=True)
    time.sleep(0.3)

print()
