# simple_calculator.py

def add(x, y):
    """두 수를 더하는 함수"""
    return x + y

def subtract(x, y):
    """두 수를 빼는 함수"""
    return x - y

def multiply(x, y):
    """두 수를 곱하는 함수"""
    return x * y

def divide(x, y):
    """두 수를 나누는 함수. 0으로 나누는 경우 예외 처리"""
    if y == 0:
        return "오류: 0으로 나눌 수 없습니다."
    return x / y

def main():
    """계산기 프로그램의 메인 함수"""
    print("간단한 계산기입니다.")
    print("연산을 선택하세요:")
    print("1. 더하기")
    print("2. 빼기")
    print("3. 곱하기")
    print("4. 나누기")

    while True:
        choice = input("선택 (1/2/3/4): ")

        if choice in ('1', '2', '3', '4'):
            try:
                num1 = float(input("첫 번째 숫자를 입력하세요: "))
                num2 = float(input("두 번째 숫자를 입력하세요: "))
            except ValueError:
                print("잘못된 입력입니다. 숫자를 입력해주세요.")
                continue

            if choice == '1':
                print(f"{num1} + {num2} = {add(num1, num2)}")
            elif choice == '2':
                print(f"{num1} - {num2} = {subtract(num1, num2)}")
            elif choice == '3':
                print(f"{num1} * {num2} = {multiply(num1, num2)}")
            elif choice == '4':
                result = divide(num1, num2)
                print(f"{num1} / {num2} = {result}")
            
            next_calculation = input("다른 계산을 하시겠습니까? (yes/no): ")
            if next_calculation.lower() != 'yes':
                break
        else:
            print("잘못된 선택입니다. 다시 시도해주세요.")

if __name__ == "__main__":
    main()
