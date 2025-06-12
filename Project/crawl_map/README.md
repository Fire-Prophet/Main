# 🔥 산불 데이터 크롤링 시스템

한국 산림청 산불관제시스템에서 실시간 산불 현황을 수집하는 Selenium 기반 크롤링 도구입니다.

## 📋 주요 기능

- **실시간 산불 현황 모니터링**: 진화중/진화완료/기타종료 현황 수집
- **스크린샷 캡처**: 전체 페이지 및 지도 영역 이미지 저장
- **자동화된 데이터 수집**: 지정된 간격으로 자동 모니터링
- **이미지 저장**: 타임스탬프별 스크린샷 관리

## 🛠️ 시스템 요구사항

### Python 환경
- Python 3.8 이상
- pip (Python 패키지 관리자)

### 브라우저
- Chrome/Chromium (Selenium용, 자동 설치)

## 📦 설치 가이드

### 1. 저장소 클론
```bash
git clone <repository-url>
cd fire_crawler
```

### 2. Python 가상환경 설정 (권장)
```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
```

### 3. Python 라이브러리 설치
```bash
# 필수 라이브러리 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install selenium==4.15.0
pip install webdriver-manager==4.0.1
pip install requests==2.31.0
```

## 🚀 사용 방법

### 기본 크롤러 실행
```bash
# Selenium 기반 크롤러 실행
python selenium_fire_crawler.py
```

### 헤드리스 모드 설정
코드 내에서 헤드리스 모드를 활성화할 수 있습니다:
```python
# selenium_fire_crawler.py에서 헤드리스 모드 활성화
chrome_options.add_argument('--headless')  # 주석 해제
```

### 주요 기능
- **실시간 현황 수집**: 진화중/진화완료/기타종료 산불 건수
- **스크린샷 저장**: 타임스탬프가 포함된 이미지 파일 생성
- **자동 지연**: 페이지 로딩 대기 시간 자동 조절

## 📊 수집 가능한 데이터

### 실시간 현황
- **진화중**: 현재 진화 작업 중인 산불 수
- **진화완료**: 완전히 진화된 산불 수  
- **산불외종료**: 기타 사유로 종료된 산불 수

### 이미지 데이터
- 전체 페이지 스크린샷
- 산불 관제 시스템 화면 캡처
- 타임스탬프별 이미지 관리

## ⚠️ 주의사항

### 법적 고려사항
- 해당 사이트의 robots.txt 확인 필요
- 과도한 요청으로 서버 부하 방지
- 개인정보 또는 민감 정보 수집 금지

### 기술적 제한
- 사이트 구조 변경 시 수정 필요
- JavaScript 기반 데이터 로딩 대응 필요

### 사용 권장사항
```python
# 적절한 지연 시간 설정
time.sleep(5)  # 5초 대기

# User-Agent 설정
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 에러 처리
try:
    data = crawler.get_fire_status_data()
except Exception as e:
    print(f"데이터 수집 실패: {e}")
```

## 🔧 고급 설정

### 헤드리스 모드 설정
```python
chrome_options = Options()
chrome_options.add_argument("--headless")  # 백그라운드 실행
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
```

### 에러 처리
```python
from selenium.common.exceptions import TimeoutException

try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cntFireExtinguish"))
    )
except TimeoutException:
    print("페이지 로딩 시간 초과")
    driver.refresh()
```

## 📞 지원

- 기술 문의: GitHub Issues
- 사용법 질문: 코드 주석 참조

---

**⚠️ 중요**: 이 도구는 교육 및 연구 목적으로 제작되었습니다. 상업적 사용이나 대량 데이터 수집 시 해당 사이트의 이용약관을 확인하고 승인을 받으시기 바랍니다.