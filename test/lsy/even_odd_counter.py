nums = list(map(int, input("숫자들을 띄어쓰기로 구분해서 입력: ").split()))
even = len([n for n in nums if n % 2 == 0])
odd = len(nums) - even
print(f"짝수: {even}개, 홀수: {odd}개")
