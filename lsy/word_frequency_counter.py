from collections import Counter
text = input("문장을 입력하세요: ")
words = text.lower().split()
freq = Counter(words)
for word, count in freq.items():
    print(f"{word}: {count}회")
