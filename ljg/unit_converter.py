# unit_converter.py

def celsius_to_fahrenheit(celsius):
    """섭씨를 화씨로 변환합니다."""
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    """화씨를 섭씨로 변환합니다."""
    return (fahrenheit - 32) * 5/9

def kg_to_pounds(kg):
    """킬로그램을 파운드로 변환합니다."""
    return kg * 2.20462

def pounds_to_kg(pounds):
    """파운드를 킬로그램으로 변환합니다."""
    return pounds / 2.20462

def meters_to_feet(meters):
    """미터를 피트로 변환합니다."""
    return meters * 3.28084

def feet_to_meters(feet):
    """피트를 미터로 변환합니다."""
    return feet / 3.28084


def main():
    """단위 변환기 메인 함수"""
    print("단위 변환기입니다.")
    
    while True:
        print("\n변환할 단위를 선택하세요:")
        print("1. 섭씨(C) -> 화씨(F)")
        print("2. 화씨(F) -> 섭씨(C)")
        print("3. 킬로그램(kg) -> 파운드(lb)")
        print("4. 파운드(lb) -> 킬로그램(kg)")
        print("5. 미터(m) -> 피트(ft)")
        print("6. 피트(ft) -> 미터(m)")
        print("7. 종료")
        
        choice = input("선택 (1-7): ")
        
        value_to_convert = None
        if choice in ('1', '2', '3', '4', '5', '6'):
            while True:
                try:
                    value_str = input("변환할 값을 입력하세요: ")
                    value_to_convert = float(value_str)
                    break
                except ValueError:
                    print("잘못된 입력입니다. 숫자를 입력해주세요.")
        
        if choice == '1':
            result = celsius_to_fahrenheit(value_to_convert)
            print(f"{value_to_convert}°C는 {result:.2f}°F 입니다.")
        elif choice == '2':
            result = fahrenheit_to_celsius(value_to_convert)
            print(f"{value_to_convert}°F는 {result:.2f}°C 입니다.")
        elif choice == '3':
            result = kg_to_pounds(value_to_convert)
            print(f"{value_to_convert}kg은(는) {result:.2f}lb 입니다.")
        elif choice == '4':
            result = pounds_to_kg(value_to_convert)
            print(f"{value_to_convert}lb은(는) {result:.2f}kg 입니다.")
        elif choice == '5':
            result = meters_to_feet(value_to_convert)
            print(f"{value_to_convert}m은(는) {result:.2f}ft 입니다.")
        elif choice == '6':
            result = feet_to_meters(value_to_convert)
            print(f"{value_to_convert}ft은(는) {result:.2f}m 입니다.")
        elif choice == '7':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 1부터 7 사이의 숫자를 입력하세요.")
            
        print("-" * 20)

if __name__ == "__main__":
    main()
