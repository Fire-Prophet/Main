# password_hasher.py
import hashlib
import os
import binascii
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def hash_password(password, salt=None, iterations=100000):
    """
    PBKDF2 HMAC-SHA256을 사용하여 비밀번호를 해시합니다.
    솔트가 주어지지 않으면 새로운 솔트를 생성합니다.
    반환 값은 'salt:hashed_password' 형식의 문자열입니다.
    """
    if not isinstance(password, str):
        logging.error("Password must be a string.")
        raise TypeError("Password must be a string.")

    if salt is None:
        salt = os.urandom(16) # 16바이트 솔트 생성
        logging.info("New salt generated for password hashing.")
    else:
        # 솔트가 문자열로 주어졌을 경우 bytes로 변환
        if isinstance(salt, str):
            salt = binascii.unhexlify(salt)
        elif not isinstance(salt, bytes):
            logging.error("Salt must be bytes or a hex string.")
            raise TypeError("Salt must be bytes or a hex string.")

    try:
        hashed_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations
        )
        hashed_password = binascii.hexlify(hashed_bytes).decode('ascii')
        salt_hex = binascii.hexlify(salt).decode('ascii')
        logging.info(f"Password hashed successfully. Iterations: {iterations}")
        return f"{salt_hex}:{hashed_password}"
    except Exception as e:
        logging.error(f"Error during password hashing: {e}")
        raise

def verify_password(stored_password_hash, provided_password, iterations=100000):
    """
    저장된 해시와 제공된 비밀번호를 비교하여 일치하는지 확인합니다.
    stored_password_hash는 'salt:hashed_password' 형식이어야 합니다.
    """
    if not isinstance(stored_password_hash, str) or ":" not in stored_password_hash:
        logging.error("Stored password hash format is incorrect. Expected 'salt:hashed_password'.")
        return False
    if not isinstance(provided_password, str):
        logging.error("Provided password must be a string.")
        return False

    try:
        salt_hex, stored_hash = stored_password_hash.split(':')
        salt = binascii.unhexlify(salt_hex)
        
        # 제공된 비밀번호로 해시를 다시 생성
        calculated_hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt,
            iterations
        )
        calculated_hash = binascii.hexlify(calculated_hash_bytes).decode('ascii')
        
        is_correct = (calculated_hash == stored_hash)
        if is_correct:
            logging.info("Password verification successful.")
        else:
            logging.warning("Password verification failed: Passwords do not match.")
        return is_correct
    except ValueError:
        logging.error("Invalid stored password hash format. Could not split salt and hash.")
        return False
    except binascii.Error as e:
        logging.error(f"Invalid hex string for salt: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during password verification: {e}")
        return False

# 예시 사용
if __name__ == "__main__":
    test_password = "MySecurePassword123!"

    # 비밀번호 해싱
    hashed_pw = hash_password(test_password)
    print(f"Hashed password: {hashed_pw}")

    # 올바른 비밀번호로 검증
    if verify_password(hashed_pw, test_password):
        print("Verification successful for correct password.")
    else:
        print("Verification failed for correct password (ERROR!).")

    # 틀린 비밀번호로 검증
    if verify_password(hashed_pw, "WrongPassword"):
        print("Verification successful for wrong password (ERROR!).")
    else:
        print("Verification failed for wrong password (correct).")

    # 다른 반복 횟수로 해싱 및 검증
    print("\n--- Testing with different iterations ---")
    hashed_pw_high_iter = hash_password(test_password, iterations=200000)
    print(f"Hashed password (200k iterations): {hashed_pw_high_iter}")
    if verify_password(hashed_pw_high_iter, test_password, iterations=200000):
        print("Verification successful with 200k iterations (correct).")
    else:
        print("Verification failed with 200k iterations (ERROR!).")
