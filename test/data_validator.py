# data_validator.py
import re
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataValidator:
    def __init__(self):
        """
        다양한 데이터 유형에 대한 유효성 검사 클래스.
        """
        logging.info("DataValidator initialized.")

    def is_valid_email(self, email_address):
        """
        주어진 문자열이 유효한 이메일 형식인지 확인합니다.
        """
        if not isinstance(email_address, str):
            logging.warning(f"Input for email validation is not a string: {type(email_address)}")
            return False
        # 매우 기본적인 이메일 정규식. 완전한 유효성 검사는 훨씬 복잡합니다.
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        result = re.fullmatch(regex, email_address) is not None
        logging.debug(f"Email '{email_address}' is valid: {result}")
        return result

    def is_valid_phone_number(self, phone_number, country_code="US"):
        """
        주어진 문자열이 유효한 전화번호 형식인지 확인합니다.
        국가 코드에 따라 다른 정규식을 사용할 수 있습니다. (현재는 US 기본)
        """
        if not isinstance(phone_number, str):
            logging.warning(f"Input for phone validation is not a string: {type(phone_number)}")
            return False

        if country_code.upper() == "US":
            # (XXX) XXX-XXXX 또는 XXX-XXX-XXXX 또는 XXXXXXXXXX
            regex = r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$'
        else:
            # 다른 국가 코드에 대한 추가 로직 또는 일반적인 패턴
            logging.warning(f"Phone number validation for country code '{country_code}' not implemented. Using general digit check.")
            regex = r'^\+?[0-9\s()-]{7,20}$' # 매우 일반적인 패턴

        result = re.fullmatch(regex, phone_number) is not None
        logging.debug(f"Phone '{phone_number}' is valid for {country_code}: {result}")
        return result

    def is_valid_password(self, password, min_length=8, require_uppercase=True,
                          require_lowercase=True, require_digit=True, require_special=True):
        """
        비밀번호가 보안 요구 사항을 충족하는지 확인합니다.
        """
        if not isinstance(password, str):
            logging.warning(f"Input for password validation is not a string: {type(password)}")
            return False

        if len(password) < min_length:
            logging.debug(f"Password too short (min {min_length}).")
            return False
        if require_uppercase and not re.search(r'[A-Z]', password):
            logging.debug("Password missing uppercase.")
            return False
        if require_lowercase and not re.search(r'[a-z]', password):
            logging.debug("Password missing lowercase.")
            return False
        if require_digit and not re.search(r'\d', password):
            logging.debug("Password missing digit.")
            return False
        if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            logging.debug("Password missing special character.")
            return False
        
        logging.debug("Password is valid.")
        return True

    def is_positive_integer(self, value):
        """
        주어진 값이 양의 정수인지 확인합니다.
        """
        result = isinstance(value, int) and value > 0
        logging.debug(f"Value {value} is positive integer: {result}")
        return result

# 예시 사용
if __name__ == "__main__":
    validator = DataValidator()

    print("--- Email Validation ---")
    print(f"'test@example.com' valid: {validator.is_valid_email('test@example.com')}")
    print(f"'invalid-email' valid: {validator.is_valid_email('invalid-email')}")
    print(f"'test@example' valid: {validator.is_valid_email('test@example')}")
    print(f"None valid: {validator.is_valid_email(None)}")

    print("\n--- Phone Number Validation (US) ---")
    print(f"'(123) 456-7890' valid: {validator.is_valid_phone_number('(123) 456-7890')}")
    print(f"'123-456-7890' valid: {validator.is_valid_phone_number('123-456-7890')}")
    print(f"'1234567890' valid: {validator.is_valid_phone_number('1234567890')}")
    print(f"'123' valid: {validator.is_valid_phone_number('123')}")

    print("\n--- Password Validation ---")
    print(f"'Password123!' valid: {validator.is_valid_password('Password123!')}")
    print(f"'password' (too simple) valid: {validator.is_valid_password('password')}")
    print(f"'Pass1!' (too short) valid: {validator.is_valid_password('Pass1!', min_length=8)}")
    print(f"'Password123' (no special) valid: {validator.is_valid_password('Password123')}")
    print(f"'password123!' (no uppercase) valid: {validator.is_valid_password('password123!')}")

    print("\n--- Positive Integer Validation ---")
    print(f"5 valid: {validator.is_positive_integer(5)}")
    print(f"0 valid: {validator.is_positive_integer(0)}")
    print(f"-10 valid: {validator.is_positive_integer(-10)}")
    print(f"3.14 valid: {validator.is_positive_integer(3.14)}")
    print(f"'abc' valid: {validator.is_positive_integer('abc')}")
