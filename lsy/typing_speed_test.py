import time

input("시작하려면 Enter를 누르세요.")
start = time.time()
text = input("다음 문장을 입력하세요:\n파이썬은 재미있는 언어입니다.\n")
end = time.time()

elapsed = end - start
print(f"걸린 시간: {elapsed:.2f}초")
