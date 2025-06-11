from collections import Counter

with open("chat_log.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

words = []
for line in lines:
    words.extend(line.strip().split())

counter = Counter(words)
summary = counter.most_common(10)

print("📝 대화 요약 (자주 등장한 단어):")
for word, freq in summary:
    print(f"{word}: {freq}회")
