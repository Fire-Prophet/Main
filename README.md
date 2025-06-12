# 산불 확산 예측 및 실시간 모니터링 시스템

<br>

> 👨‍💻 **프로젝트 한 줄 요약**: 실시간 데이터(산불 위치, 기상)를 기반으로 산불의 확산 경로를 시뮬레이션하고, 다양한 GIS 데이터를 중첩하여 보여주는 웹 기반 모니터링 시스템입니다.



<br>

## ✨ 주요 기능

### 🗺️ 프론트엔드 (React & OpenLayers)
- **실시간 산불 위치 시각화**: Selenium 크롤러가 수집한 전국의 산불 발생 위치를 지도 위에 실시간으로 표시합니다.
- **클릭 기반 시뮬레이션 실행**: 사용자가 지도 위의 격자를 클릭하여 발화점으로 지정하면, 해당 지점의 산불 확산 시뮬레이션을 시작합니다.
- **시간에 따른 확산 과정 시각화**:
    - **연소 상태**: 시간에 따라 `연소 완료`, `연소 중`, `확산 예상` 지점을 각각 다른 색상으로 표현합니다.
    - **확산 경계**: 10분 간격으로 예상 확산 범위를 폴리곤(Polygon) 형태로 시각화하여 직관성을 높였습니다.
- **타임라인 컨트롤**: 슬라이더를 통해 시뮬레이션 시간을 자유롭게 조절하며 특정 시점의 확산 상태를 확인할 수 있습니다.
- **다중 GIS 레이어**: 임상도, 토양도, 등산로, 연료 등급 등 다양한 보조 레이어를 사용자가 직접 켜고 끄거나 투명도를 조절할 수 있습니다.
- **실시간 기상 정보**: 지도 위의 산악기상관측소 마커를 클릭하면 Firebase와 연동된 실시간 기상 정보(온도, 습도, 풍향/풍속)를 조회합니다.
- **사용자 친화적 범례**: 현재 활성화된 레이어의 정보만 보여주는 동적 범례를 제공하며, 드래그하여 위치를 자유롭게 이동할 수 있습니다.

### ⚙️ 백엔드 (Node.js & Express)
- **산불 확산 예측 API**:
    - 발화점 ID를 입력받아 정교한 산불 확산 시뮬레이션을 수행하고 결과를 JSON 형태로 반환합니다.
    - 시뮬레이션은 **연료량(임상도)**, **경사도(토양도)**, **건조도(토양, 습도)**, **바람(풍향/풍속)** 등 복합적인 요인을 고려하여 계산됩니다.
    - 계산 결과는 각 격자의 예상 발화/연소 시간 및 시간대별 확산 경계(Convex Hull)를 포함합니다.
- **데이터 API 및 정적 파일 제공**:
    - 시뮬레이션에 필요한 격자 데이터 및 연료 등급 데이터를 제공하는 API를 운영합니다.
    - Python 크롤러가 수집한 `fire_markers.json` 파일을 프론트엔드에 제공합니다.
    - 빌드된 React 앱을 정적으로 호스팅하여 단일 서버로 전체 서비스를 운영합니다.

### 📡 데이터 수집 (Python & Node.js)
- **실시간 산불 위치 크롤링**: `selenium_fire_crawler.py` 스크립트가 주기적으로 산림청 사이트를 크롤링하여 지도 이미지상의 마커를 분석하고, `fire_markers.json` 파일로 저장합니다.
- **실시간 산악 기상 수집**: `updateFirebaseWeather.js` 스크립트가 주기적으로 기상청 API에서 날씨 정보를 조회하여 Firebase Realtime Database에 업데이트합니다.

<br>

├── backend/                  # 백엔드 서버 (Node.js & Express)
│   ├── config/
│   │   └── db.js             # DB 커넥션 풀 설정
│   ├── routes/
│   │   └── apiRoutes.js      # API 라우트 정의
│   ├── services/
│   │   └── simulationService.js # 핵심 산불 확산 시뮬레이션 로직
│   └── apiServer.js          # Express 메인 서버 파일
├── firefighter/              # 프론트엔드 (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── VWorldMap.js  # 메인 지도 컴포넌트
│   │   │   ├── Legend.js     # 범례 컴포넌트
│   │   │   ├── mapConfig.js  # 지도 레이어 및 스타일 설정
│   │   │   └── ...
│   │   └── firebaseConfig.js # Firebase 초기화 설정
│   └── package.json
├── shared_data/              # 크롤러와 서버 간 공유 데이터 폴더
│   └── fire_markers.json     # 실시간 산불 위치 데이터 (JSON)
└── (root)
├── selenium_fire_crawler.py # 산불 위치 크롤러 (Python)
└── updateFirebaseWeather.js # 기상 정보 수집기 (Node.js)


<br>

## ⚙️ 설치 및 실행 방법

### 1. 사전 준비

- **Node.js & npm**
- **Python & pip**
- **MySQL** (또는 MariaDB)
- **Google Chrome & ChromeDriver** (버전 일치 확인)
- **Firebase** 프로젝트 생성 및 `serviceAccountKey.json` 다운로드

### 2. 백엔드 설정
# 1. DB에 접속하여 데이터베이스 및 테이블 생성, 데이터 임포트

# 2. 백엔드 폴더로 이동 및 의존성 설치
```
cd backend
npm install
```

# 3. .env 파일 생성 및 DB 정보 입력
```
# .env 파일 예시
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=your_database
```

# 4. 프론트엔드 설정
```
# 프론트엔드 폴더로 이동 및 의존성 설치
cd firefighter
npm install

# src/firebaseConfig.js 파일에 Firebase 프로젝트 설정 정보 입력
```

# 5. 데이터 수집 스크립트 설정
```
# 1. 루트 폴더에서 Python 의존성 설치
pip install selenium pillow apscheduler requests

# 2. 루트 폴더에서 Node.js 의존성 설치
npm install firebase-admin axios

# 3. 루트 폴더에 Firebase 서비스 계정 키 파일(serviceAccountKey.json) 위치
# 4. selenium_fire_crawler.py 파일의 driver_path 변수에 ChromeDriver 경로 설정
# 5. updateFirebaseWeather.js 파일의 KMA_API_KEY 변수에 기상청 API 키 입력
```

# 6 시스템 실행
주의: 각 스크립트는 별도의 터미널에서 실행해야 합니다.
```
# 터미널 1: 날씨 정보 수집기 실행
node updateFirebaseWeather.js

# 터미널 2: 산불 위치 크롤러 실행
python selenium_fire_crawler.py

# 터미널 3: 백엔드 서버 실행
cd backend
node apiServer.js

# 터미널 4: 프론트엔드 개발 서버 실행
cd firefighter
npm start
```

🌐 API 엔드포인트
POST /api/predict-fire-spread

설명: 특정 지점의 산불 확산을 시뮬레이션합니다.
Request Body: { "ignition_id": number }
Response: 시뮬레이션 결과 (발화/연소 시간, 확산 경계 등)을 담은 GeoJSON
GET /api/mapped-grid-data

설명: 지도에 표시할 전국 격자점 데이터를 GeoJSON 형식으로 반환합니다.
GET /api/grid-with-fuel-info

설명: 각 격자점의 위치와 연료 등급 점수를 GeoJSON 형식으로 반환합니다.





