# math_operations.py
import math
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_square_root(number):
    """
    주어진 숫자의 제곱근을 계산합니다. 음수 입력 시 ValueError를 발생시킵니다.
    """
    if number < 0:
        logging.error(f"Attempted to calculate square root of a negative number: {number}")
        raise ValueError("Cannot calculate square root of a negative number.")
    result = math.sqrt(number)
    logging.info(f"Calculated square root of {number}: {result}")
    return result

def calculate_factorial(number):
    """
    주어진 숫자의 팩토리얼을 계산합니다. 음수 입력 시 ValueError를 발생시킵니다.
    """
    if not isinstance(number, int) or number < 0:
        logging.error(f"Invalid input for factorial: {number}. Must be a non-negative integer.")
        raise ValueError("Input for factorial must be a non-negative integer.")
    if number == 0:
        return 1
    result = math.factorial(number)
    logging.info(f"Calculated factorial of {number}: {result}")
    return result

def calculate_circumference(radius):
    """
    주어진 반지름의 원의 둘레를 계산합니다.
    """
    if radius < 0:
        logging.warning(f"Calculating circumference with a negative radius: {radius}. Treating as positive.")
        radius = abs(radius)
    result = 2 * math.pi * radius
    logging.info(f"Calculated circumference for radius {radius}: {result}")
    return result

def power_of_two(exponent):
    """
    2의 거듭제곱을 계산합니다.
    """
    result = 2 ** exponent
    logging.info(f"Calculated 2 to the power of {exponent}: {result}")
    return result

# 예시 사용
if __name__ == "__main__":
    try:
        print(f"Square root of 16: {calculate_square_root(16)}")
        print(f"Factorial of 5: {calculate_factorial(5)}")
        print(f"Circumference with radius 10: {calculate_circumference(10)}")
        print(f"2 to the power of 8: {power_of_two(8)}")
        # 에러 발생 예시
        # print(f"Square root of -4: {calculate_square_root(-4)}")
        # print(f"Factorial of -3: {calculate_factorial(-3)}")
    except ValueError as e:
        print(f"Error: {e}")
