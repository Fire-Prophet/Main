def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

num = int(input("숫자를 입력하세요: "))
print(f"{num}은(는) 소수입니다." if is_prime(num) else f"{num}은(는) 소수가 아닙니다.")
