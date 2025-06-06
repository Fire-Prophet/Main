def calc(a, b, op):
    if op == '+': return a + b
    elif op == '-': return a - b
    elif op == '*': return a * b
    elif op == '/': return a / b
    else: return "잘못된 연산자입니다."

a = float(input("첫 번째 숫자: "))
b = float(input("두 번째 숫자: "))
op = input("연산자(+ - * /): ")
print("결과:", calc(a, b, op))
