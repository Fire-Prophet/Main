import os
files = [f for f in os.listdir() if f.endswith('.py')]
print("파이썬 파일 목록:", files)
