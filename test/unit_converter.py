# unit_converter.py
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UnitConverter:
    def __init__(self):
        """
        단위 변환을 위한 클래스 초기화.
        """
        self.conversion_rates = {
            "length": {
                "meter": 1.0,
                "kilometer": 1000.0,
                "centimeter": 0.01,
                "millimeter": 0.001,
                "mile": 1609.34,
                "yard": 0.9144,
                "foot": 0.3048,
                "inch": 0.0254
            },
            "weight": {
                "kilogram": 1.0,
                "gram": 0.001,
                "pound": 0.453592,
                "ounce": 0.0283495
            },
            "temperature": { # Special handling for temperature
                "celsius": "C",
                "fahrenheit": "F",
                "kelvin": "K"
            }
        }
        logging.info("UnitConverter initialized with standard conversion rates.")

    def convert_length(self, value, from_unit, to_unit):
        """
        길이 단위를 변환합니다.
        """
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        if from_unit not in self.conversion_rates["length"] or \
           to_unit not in self.conversion_rates["length"]:
            logging.error(f"Invalid length units: {from_unit} or {to_unit}")
            raise ValueError("Invalid length units provided.")

        base_value = value * self.conversion_rates["length"][from_unit]
        converted_value = base_value / self.conversion_rates["length"][to_unit]
        logging.info(f"Converted {value} {from_unit} to {converted_value} {to_unit}.")
        return converted_value

    def convert_weight(self, value, from_unit, to_unit):
        """
        무게 단위를 변환합니다.
        """
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        if from_unit not in self.conversion_rates["weight"] or \
           to_unit not in self.conversion_rates["weight"]:
            logging.error(f"Invalid weight units: {from_unit} or {to_unit}")
            raise ValueError("Invalid weight units provided.")

        base_value = value * self.conversion_rates["weight"][from_unit]
        converted_value = base_value / self.conversion_rates["weight"][to_unit]
        logging.info(f"Converted {value} {from_unit} to {converted_value} {to_unit}.")
        return converted_value

    def convert_temperature(self, value, from_unit, to_unit):
        """
        온도 단위를 변환합니다 (섭씨, 화씨, 켈빈).
        """
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        if from_unit not in self.conversion_rates["temperature"] or \
           to_unit not in self.conversion_rates["temperature"]:
            logging.error(f"Invalid temperature units: {from_unit} or {to_unit}")
            raise ValueError("Invalid temperature units provided.")

        # 모두 섭씨로 변환 후, 다시 목표 단위로 변환
        if from_unit == "celsius":
            temp_celsius = value
        elif from_unit == "fahrenheit":
            temp_celsius = (value - 32) * 5/9
        elif from_unit == "kelvin":
            temp_celsius = value - 273.15
        else:
            raise ValueError("Unknown 'from' temperature unit.")

        if to_unit == "celsius":
            converted_value = temp_celsius
        elif to_unit == "fahrenheit":
            converted_value = (temp_celsius * 9/5) + 32
        elif to_unit == "kelvin":
            converted_value = temp_celsius + 273.15
        else:
            raise ValueError("Unknown 'to' temperature unit.")
        
        logging.info(f"Converted {value} {from_unit} to {converted_value} {to_unit}.")
        return converted_value

# 예시 사용
if __name__ == "__main__":
    converter = UnitConverter()

    print("--- Length Conversions ---")
    print(f"10 meters to kilometers: {converter.convert_length(10, 'meter', 'kilometer'):.4f} km")
    print(f"5 miles to meters: {converter.convert_length(5, 'mile', 'meter'):.2f} m")
    print(f"12 inches to centimeters: {converter.convert_length(12, 'inch', 'centimeter'):.2f} cm")

    print("\n--- Weight Conversions ---")
    print(f"1000 grams to kilograms: {converter.convert_weight(1000, 'gram', 'kilogram'):.2f} kg")
    print(f"2 pounds to grams: {converter.convert_weight(2, 'pound', 'gram'):.2f} g")

    print("\n--- Temperature Conversions ---")
    print(f"25 Celsius to Fahrenheit: {converter.convert_temperature(25, 'celsius', 'fahrenheit'):.2f} F")
    print(f"68 Fahrenheit to Celsius: {converter.convert_temperature(68, 'fahrenheit', 'celsius'):.2f} C")
    print(f"0 Celsius to Kelvin: {converter.convert_temperature(0, 'celsius', 'kelvin'):.2f} K")
    print(f"300 Kelvin to Celsius: {converter.convert_temperature(300, 'kelvin', 'celsius'):.2f} C")
