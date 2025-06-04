# api_authenticator.py
import requests
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class APIAuthenticator:
    def __init__(self, auth_url, username=None, password=None, api_key=None):
        """
        API 인증을 위한 클래스 초기화.
        지원되는 인증 방식: username/password (예: OAuth 토큰), API 키.
        """
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.api_key = api_key
        self.token = None
        self.headers = {}
        logging.info(f"APIAuthenticator initialized for {auth_url}.")

    def authenticate_with_password(self):
        """
        사용자 이름과 비밀번호로 인증하고 토큰을 얻습니다 (예: OAuth 2.0).
        이것은 예시이며, 실제 API의 인증 흐름에 따라 구현해야 합니다.
        """
        if not self.username or not self.password:
            logging.error("Username and password are required for password authentication.")
            return False
        try:
            # 실제 API는 이와 다를 수 있습니다 (grant_type, client_id 등).
            payload = {"username": self.username, "password": self.password}
            response = requests.post(self.auth_url, json=payload, timeout=10)
            response.raise_for_status() # 200 이외의 상태 코드에 대해 예외 발생
            auth_data = response.json()
            self.token = auth_data.get("access_token")
            if self.token:
                self.headers['Authorization'] = f"Bearer {self.token}"
                logging.info("Successfully authenticated with username/password and obtained token.")
                return True
            else:
                logging.error("Authentication successful but no access_token found in response.")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"Authentication with password failed: {e}")
            self.token = None
            self.headers = {}
            return False

    def set_api_key_header(self, header_name="X-API-Key"):
        """
        API 키를 사용하여 요청 헤더를 설정합니다.
        """
        if self.api_key:
            self.headers[header_name] = self.api_key
            logging.info(f"API Key set in header '{header_name}'.")
            return True
        else:
            logging.warning("API key not provided for setting header.")
            return False

    def get_auth_headers(self):
        """
        현재 인증된 헤더를 반환합니다.
        """
        return self.headers

    def test_authenticated_request(self, target_url):
        """
        설정된 헤더를 사용하여 인증된 요청을 시도합니다.
        """
        if not self.headers:
            logging.warning("No authentication headers set. Request will be unauthenticated.")
        try:
            logging.info(f"Testing authenticated request to {target_url} with headers: {self.headers}")
            response = requests.get(target_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logging.info(f"Authenticated request successful. Status: {response.status_code}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Authenticated request failed: {e}")
            return None

# 예시 사용
if __name__ == "__main__":
    # 이 부분은 실제 API 인증 URL과 키로 대체해야 합니다.
    # 더미 URL을 사용하므로 실제 인증은 실패할 수 있습니다.
    AUTH_URL_DUMMY = "https://api.example.com/auth/token"
    API_KEY_DUMMY = "my_secret_api_key_123"
    TARGET_API_URL_DUMMY = "https://api.example.com/data/protected"

    # API 키 인증 예시
    print("--- API Key Authentication Example ---")
    api_auth = APIAuthenticator(auth_url=AUTH_URL_DUMMY, api_key=API_KEY_DUMMY)
    api_auth.set_api_key_header() # 기본 헤더 이름 사용
    print("Authentication Headers:", api_auth.get_auth_headers())
    # test_authenticated_request는 실제 API가 없으므로 실행되지 않습니다.
    # print("Test authenticated request (API Key):", api_auth.test_authenticated_request(TARGET_API_URL_DUMMY))


    # 사용자 이름/비밀번호 인증 예시 (더미)
    print("\n--- Username/Password Authentication Example (Dummy) ---")
    user_auth = APIAuthenticator(auth_url=AUTH_URL_DUMMY, username="testuser", password="testpassword")
    # authenticate_with_password는 실제 API 엔드포인트가 아니므로 실패할 것입니다.
    if user_auth.authenticate_with_password():
        print("Authentication successful!")
        print("Authentication Headers:", user_auth.get_auth_headers())
        # print("Test authenticated request (Token):", user_auth.test_authenticated_request(TARGET_API_URL_DUMMY))
    else:
        print("Authentication failed (as expected with dummy URL).")
