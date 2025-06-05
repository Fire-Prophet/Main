# http_client.py
import requests
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HttpClient:
    def __init__(self, base_url="", timeout=10):
        """
        HTTP 클라이언트 초기화.
        """
        self.base_url = base_url
        self.timeout = timeout
        logging.info(f"HttpClient initialized with base URL: {base_url}, timeout: {timeout}s.")

    def _make_request(self, method, url, **kwargs):
        """
        내부적으로 HTTP 요청을 수행합니다.
        """
        full_url = f"{self.base_url}{url}" if self.base_url else url
        logging.info(f"Making {method.upper()} request to {full_url}")
        try:
            response = requests.request(method, full_url, timeout=self.timeout, **kwargs)
            response.raise_for_status()  # 200 이외의 상태 코드에 대해 예외 발생
            logging.info(f"Request to {full_url} successful. Status: {response.status_code}")
            return response
        except requests.exceptions.Timeout:
            logging.error(f"Request to {full_url} timed out after {self.timeout}s.")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Request to {full_url} failed: {e}")
            raise

    def get(self, url, params=None, headers=None):
        """
        GET 요청을 수행합니다.
        """
        return self._make_request('GET', url, params=params, headers=headers)

    def post(self, url, data=None, json_data=None, headers=None):
        """
        POST 요청을 수행합니다.
        """
        return self._make_request('POST', url, data=data, json=json_data, headers=headers)

    def put(self, url, data=None, json_data=None, headers=None):
        """
        PUT 요청을 수행합니다.
        """
        return self._make_request('PUT', url, data=data, json=json_data, headers=headers)

    def delete(self, url, headers=None):
        """
        DELETE 요청을 수행합니다.
        """
        return self._make_request('DELETE', url, headers=headers)

# 예시 사용
if __name__ == "__main__":
    client = HttpClient(base_url="https://jsonplaceholder.typicode.com")

    try:
        # GET 요청 예시
        response_get = client.get("/posts/1")
        print("GET Response (post 1):\n", json.dumps(response_get.json(), indent=2))

        # POST 요청 예시
        new_post = {"title": "foo", "body": "bar", "userId": 1}
        response_post = client.post("/posts", json_data=new_post)
        print("\nPOST Response (new post):\n", json.dumps(response_post.json(), indent=2))

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
