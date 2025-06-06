import requests
from bs4 import BeautifulSoup

url = "https://www.weather.go.kr/w/index.do"  # 기상청 메인 (단순 예시)
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    print("✔️ 날씨 페이지 접근 성공 (데이터 파싱 생략)")
else:
    print("❌ 날씨 정보 불러오기 실패")
