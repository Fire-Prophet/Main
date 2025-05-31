import Foundation // Foundation 프레임워크 임포트

// 온도 변환 로직을 캡슐화하는 enum
enum TemperatureUnit {
    case celsius
    case fahrenheit
    case kelvin

    // 단위를 나타내는 문자열
    var abbreviation: String {
        switch self {
        case .celsius: return "°C"
        case .fahrenheit: return "°F"
        case .kelvin: return "K"
        }
    }
}

// 온도 구조체
struct Temperature {
    var value: Double
    var unit: TemperatureUnit

    // 섭씨에서 화씨로 변환
    func toFahrenheit() -> Temperature {
        switch unit {
        case .celsius:
            return Temperature(value: (value * 9/5) + 32, unit: .fahrenheit)
        case .fahrenheit:
            return self // 이미 화씨
        case .kelvin:
            // 켈빈 -> 섭씨 -> 화씨
            let celsiusValue = value - 273.15
            return Temperature(value: (celsiusValue * 9/5) + 32, unit: .fahrenheit)
        }
    }

    // 화씨에서 섭씨로 변환
    func toCelsius() -> Temperature {
        switch unit {
        case .celsius:
            return self // 이미 섭씨
        case .fahrenheit:
            return Temperature(value: (value - 32) * 5/9, unit: .celsius)
        case .kelvin:
            return Temperature(value: value - 273.15, unit: .celsius)
        }
    }

    // 섭씨에서 켈빈으로 변환
    func toKelvin() -> Temperature {
        switch unit {
        case .celsius:
            return Temperature(value: value + 273.15, unit: .kelvin)
        case .fahrenheit:
            // 화씨 -> 섭씨 -> 켈빈
            let celsiusValue = (value - 32) * 5/9
            return Temperature(value: celsiusValue + 273.15, unit: .kelvin)
        case .kelvin:
            return self // 이미 켈빈
        }
    }

    // 온도 정보 출력
    func describe() {
        print(String(format: "%.2f%@", value, unit.abbreviation))
    }
}

// 사용자 입력을 위한 함수
func getInput(prompt: String) -> String {
    print(prompt, terminator: "") // 줄바꿈 없이 프롬프트 출력
    return readLine() ?? "" // 사용자 입력 읽기
}

// 메인 실행 로직
func main() {
    print("=== 온도 변환기 ===")
    print("변환할 온도를 입력하세요.")
    
    // 온도 값 입력 받기
    guard let valueString = getInput(prompt: "값: ").trimmingCharacters(in: .whitespacesAndNewlines),
          let value = Double(valueString) else {
        print("오류: 유효하지 않은 온도 값입니다.")
        return
    }

    // 단위 입력 받기
    let unitString = getInput(prompt: "단위 (C: 섭씨, F: 화씨, K: 켈빈): ").uppercased().trimmingCharacters(in: .whitespacesAndNewlines)
    
    var originalUnit: TemperatureUnit
    switch unitString {
    case "C": originalUnit = .celsius
    case "F": originalUnit = .fahrenheit
    case "K": originalUnit = .kelvin
    default:
        print("오류: 유효하지 않은 단위입니다. (C, F, K 중 하나를 입력하세요)")
        return
    }

    let originalTemp = Temperature(value: value, unit: originalUnit)
    print("\n--- 원본 온도 ---")
    originalTemp.describe()

    print("\n--- 변환 결과 ---")
    
    // 다른 단위로 변환 및 출력
    let convertedToCelsius = originalTemp.toCelsius()
    if convertedToCelsius.unit != originalTemp.unit || convertedToCelsius.value != originalTemp.value { // 이미 같은 단위가 아니면 출력
        print("섭씨: ", terminator: "")
        convertedToCelsius.describe()
    } else if originalTemp.unit == .celsius {
        print("이미 섭씨입니다.")
    }


    let convertedToFahrenheit = originalTemp.toFahrenheit()
    if convertedToFahrenheit.unit != originalTemp.unit || convertedToFahrenheit.value != originalTemp.value {
        print("화씨: ", terminator: "")
        convertedToFahrenheit.describe()
    } else if originalTemp.unit == .fahrenheit {
        print("이미 화씨입니다.")
    }

    let convertedToKelvin = originalTemp.toKelvin()
    if convertedToKelvin.unit != originalTemp.unit || convertedToKelvin.value != originalTemp.value {
        print("켈빈: ", terminator: "")
        convertedToKelvin.describe()
    } else if originalTemp.unit == .kelvin {
        print("이미 켈빈입니다.")
    }

    print("\n프로그램 종료.")
}

// Swift 스크립트로 실행 시 main 함수 호출
main()
