#include <iostream> // 입출력 스트림을 위한 헤더
#include <limits>   // numeric_limits를 위한 헤더

// Calculator 클래스 정의
class Calculator {
public:
    // 덧셈 메서드
    double add(double a, double b) {
        return a + b;
    }

    // 뺄셈 메서드
    double subtract(double a, double b) {
        return a - b;
    }

    // 곱셈 메서드
    double multiply(double a, double b) {
        return a * b;
    }

    // 나눗셈 메서드
    double divide(double a, double b) {
        if (b == 0) {
            // 0으로 나누는 경우 예외 처리
            std::cerr << "오류: 0으로 나눌 수 없습니다." << std::endl;
            return 0.0; // 또는 예외를 던질 수 있습니다.
        }
        return a / b;
    }

    // 사용자 입력을 받아 계산을 수행하는 함수
    void performCalculation() {
        double num1, num2;
        char op;

        std::cout << "간단한 콘솔 계산기" << std::endl;
        std::cout << "------------------" << std::endl;

        while (true) {
            std::cout << "\n첫 번째 숫자 입력 (종료하려면 'q' 입력): ";
            std::cin >> num1;

            if (std::cin.fail()) { // 입력 실패 (숫자가 아닌 문자 입력 등)
                std::cin.clear(); // 오류 플래그 초기화
                std::string input_str;
                std::cin >> input_str; // 잘못된 입력 읽어내기
                if (input_str == "q" || input_str == "Q") {
                    std::cout << "계산기를 종료합니다." << std::endl;
                    break;
                } else {
                    std::cerr << "오류: 유효하지 않은 숫자 입력입니다. 다시 시도하세요." << std::endl;
                    // 입력 버퍼 비우기 (다음 입력을 위해)
                    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                    continue;
                }
            }
            
            std::cout << "연산자 (+, -, *, /) 입력: ";
            std::cin >> op;

            std::cout << "두 번째 숫자 입력: ";
            std::cin >> num2;

            if (std::cin.fail()) {
                std::cin.clear();
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                std::cerr << "오류: 유효하지 않은 숫자 입력입니다. 다시 시도하세요." << std::endl;
                continue;
            }

            double result;
            switch (op) {
                case '+':
                    result = add(num1, num2);
                    std::cout << "결과: " << num1 << " + " << num2 << " = " << result << std::endl;
                    break;
                case '-':
                    result = subtract(num1, num2);
                    std::cout << "결과: " << num1 << " - " << num2 << " = " << result << std::endl;
                    break;
                case '*':
                    result = multiply(num1, num2);
                    std::cout << "결과: " << num1 << " * " << num2 << " = " << result << std::endl;
                    break;
                case '/':
                    result = divide(num1, num2);
                    if (num2 != 0) { // 0으로 나눈 오류 메시지는 divide 함수에서 처리
                        std::cout << "결과: " << num1 << " / " << num2 << " = " << result << std::endl;
                    }
                    break;
                default:
                    std::cerr << "오류: 유효하지 않은 연산자입니다. (+, -, *, / 중 하나를 입력하세요)" << std::endl;
                    break;
            }
            // 다음 입력을 위해 입력 버퍼 비우기
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        }
    }
};

int main() {
    Calculator calc;
    calc.performCalculation();
    return 0;
}
