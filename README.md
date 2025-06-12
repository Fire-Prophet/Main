산불 확산 예측 및 실시간 모니터링 시스템
1. 개요
본 프로젝트는 산불 발생 시 실시간 데이터를 기반으로 확산 경로를 예측하고, 다양한 관련 정보를 지도 위에 시각화하여 효과적인 대응을 지원하는 시스템입니다.

사용자는 지도 위의 특정 격자 지점을 발화점으로 선택하여 산불 확산 시뮬레이션을 실행할 수 있으며, 시간에 따른 확산 범위와 연소 상태 변화를 직관적으로 확인할 수 있습니다. 또한, 실시간으로 수집되는 산불 발생 위치와 산악 기상 데이터를 제공하여 종합적인 상황 판단을 돕습니다.

2. 주요 기능
Frontend / 시각화 (React & OpenLayers)
VWorld 지도 연동: 대한민국의 VWorld 지도를 기본 배경으로 사용합니다.
실시간 산불 위치 표시: Selenium 크롤러가 수집한 전국의 산불 발생 위치(의심, 진화 중, 진화 완료)를 지도 위에 마커로 실시간 표시합니다.
산불 확산 시뮬레이션 시각화:
사용자가 지도 위의 격자를 클릭하여 발화점으로 지정하고 시뮬레이션을 실행합니다.
시간의 흐름에 따라 연소 완료, 연소 중, 확산 예상 지점을 각기 다른 색상으로 표현합니다.
시간대별 예상 확산 범위를 폴리곤(Polygon) 형태로 시각화합니다.
타임라인 컨트롤: 슬라이더와 버튼을 통해 시뮬레이션 시간을 조절하며 특정 시점의 확산 상태를 확인할 수 있습니다.
다중 레이어 컨트롤:
임상도, 토양도, 등산로, 연료 등급 지도 등 다양한 중첩 레이어를 사용자가 직접 켜고 끌 수 있습니다.
각 레이어의 투명도를 조절하여 가시성을 확보할 수 있습니다.
산악 기상 정보 조회: 지도 위의 산악기상관측소 마커를 클릭하면 Firebase와 연동된 실시간 기상 정보(온도, 습도, 풍향, 풍속)를 조회할 수 있습니다.
동적 범례: 현재 활성화된 레이어의 정보만을 보여주는 동적 범례를 제공하며, 드래그하여 위치를 옮길 수 있습니다.
Backend / 데이터 처리 (Node.js & Express)
산불 확산 예측 API:
POST /api/predict-fire-spread
발화점 ID를 입력받아 정교한 산불 확산 시뮬레이션을 수행하고 결과를 반환합니다.
시뮬레이션은 지점의 연료량(임상도 기반), 경사도(토양도 기반), 건조도(토양 및 실시간 습도), 바람(실시간 풍향/풍속) 등 복합적인 요인을 고려하여 계산됩니다.
계산된 결과는 각 격자점의 예상 발화 시간, 연소 완료 시간 및 시간대별 확산 경계(Convex Hull)를 포함합니다.
정적 데이터 제공:
GET /api/mapped-grid-data: 시뮬레이션 발화점 선택을 위한 전국 격자 데이터를 제공합니다.
GET /api/grid-with-fuel-info: 임상도 기반으로 미리 계산된 연료 등급 정보를 격자 데이터와 함께 제공합니다.
GET /data/*: Python 크롤러가 수집한 fire_markers.json 파일을 프론트엔드에 제공하는 정적 파일 서버 역할을 합니다.
React 앱 호스팅: 빌드된 React 애플리케이션 파일을 정적으로 호스팅하여 단일 서버로 전체 서비스가 가능하도록 구성합니다.
Data Collection / 외부 데이터 연동
실시간 산불 위치 크롤링 (Python & Selenium):
selenium_fire_crawler.py 스크립트가 주기적으로 산림청 산불상황관제시스템 사이트를 크롤링합니다.
지도 캔버스(Canvas)를 스크린샷하여 이미지 프로세싱을 통해 마커의 색상(빨강, 초록, 회색)과 위치를 분석합니다.
추출된 마커 정보를 위경도 좌표로 변환하여 shared_data/fire_markers.json 파일로 저장합니다.
실시간 산악 기상 데이터 수집 (Node.js):
updateFirebaseWeather.js 스크립트가 주기적으로 기상청 API에서 전국 산악기상관측소의 날씨 정보를 조회합니다.
수집된 최신 날씨 데이터를 Firebase Realtime Database에 업데이트하여 시뮬레이션 및 프론트엔드에서 활용할 수 있도록 합니다.

4. 시스템 아키텍처
                  +--------------------------+        +--------------------------+
                  |  산림청 산불상황관제시스템  |        |      기상청 날씨 API      |
                  +--------------------------+        +--------------------------+
                           |  (Scraping)                             |  (API Call)
                           v                                        v
+------------------------------------+      +-----------------------------------------+
| selenium_fire_crawler.py (Python)  |      | updateFirebaseWeather.js (Node.js)      |
+------------------------------------+      +-----------------------------------------+
                           |                                        |
      (Saves to file)      |                                        | (Updates data)
                           v                                        v
+------------------------------------+      +-----------------------------------------+
| shared_data/fire_markers.json      |      |      Firebase Realtime Database         |
+------------------------------------+      +-----------------------------------------+
       |             ^                                 ^                  ^
(Serves file)        | (Reads Data)                  |                  | (Reads Weather)
       |             |                                 | (Reads Weather)  |
+------v-----------------------------------------------+------------------v-------------+
|                                    Backend (apiServer.js)                              |
|----------------------------------------------------------------------------------------|
| - Express.js Server                                                                    |
| - /api/predict-fire-spread (Simulation Engine - simulationService.js)                  |<-->+-----------------+
| - /api/mapped-grid-data                                                                |    |  MySQL/MariaDB  |
| - /api/grid-with-fuel-info                                                             |    | (Grid/Forest/   |
| - Serves React Build Files & Static Data                                               |    |  Soil Data)     |
+----------------------------------------------------------------------------------------+    +-----------------+
                           ^                                  ^
          (API Requests)   |                                  | (Serves App)
                           |                                  |
+--------------------------v----------------------------------v---------------------------+
|                        Frontend (VWorldMap.js - React & OpenLayers)                      |
|----------------------------------------------------------------------------------------|
| - Map Visualization & Layer Control                                                    |
| - Fetches /data/fire_markers.json for live markers                                     |
| - User triggers simulation -> Calls /api/predict-fire-spread                           |
| - Subscribes to Firebase for live weather data                                         |
+----------------------------------------------------------------------------------------+
                           ^
                           |
+--------------------------v--------------------------+
|                          User                      |
+----------------------------------------------------+

4. 기술 스택
Backend: Node.js, Express.js
Frontend: React, OpenLayers
Database: MySQL (or MariaDB), Firebase Realtime Database
Web Crawling: Python, Selenium, Pillow, APScheduler
GIS: GeoServer (WMS 레이어 제공), Turf.js (공간 분석)
Deployment: Express 정적 파일 호스팅
5. 프로젝트 구조
.
├── backend/                  # 백엔드 서버 관련 파일
│   ├── config/
│   │   └── db.js             # DB 커넥션 풀 설정
│   ├── firebaseAdmin.js      # Firebase Admin SDK 초기화 (simulationService에서 사용)
│   ├── routes/
│   │   └── apiRoutes.js      # API 라우트 정의
│   ├── services/
│   │   └── simulationService.js # 핵심 산불 확산 시뮬레이션 로직
│   ├── apiServer.js          # Express 메인 서버 파일
│   └── ...
├── firefighter/              # 프론트엔드 React 앱
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VWorldMap.js      # 메인 지도 컴포넌트
│   │   │   ├── Legend.js         # 범례 컴포넌트
│   │   │   ├── mapConfig.js      # 지도 레이어 및 스타일 설정
│   │   │   ├── weatherService.js # Firebase 날씨 데이터 구독 서비스
│   │   │   └── ...
│   │   └── ...
│   └── package.json
├── shared_data/              # 크롤러와 서버 간 공유 데이터
│   └── fire_markers.json     # 실시간 산불 위치 데이터
├── standalone_scripts/       # 독립 실행 스크립트
│   ├── selenium_fire_crawler.py # 산불 위치 크롤러 (Python)
│   └── updateFirebaseWeather.js # 기상 정보 수집기 (Node.js)
└── README.md                 # 프로젝트 설명 파일
6. 설치 및 실행 방법
사전 준비
Node.js & npm: 설치
Python & pip: 설치
MySQL/MariaDB: DB 서버 설치 및 실행
Google Chrome & ChromeDriver: Selenium이 사용할 브라우저와 드라이버 설치 (버전 일치 필요)
Firebase Project: Firebase 프로젝트 생성 및 Realtime Database 활성화, 서비스 계정 키(serviceAccountKey.json) 다운로드
1. Backend 설정
DB 준비:

MySQL/MariaDB에 접속하여 데이터베이스를 생성합니다. (예: CREATE DATABASE fire_db;)
필요한 테이블(격자, 임상도, 토양도 등)을 생성하고 데이터를 임포트합니다.
의존성 설치 및 환경 변수 설정:

Bash

cd backend
npm install

# .env 파일 생성 및 편집
# 예시:
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=fire_db
2. Frontend 설정
Bash

cd firefighter
npm install
3. 데이터 수집 스크립트 설정
날씨 정보 수집기 (updateFirebaseWeather.js):

standalone_scripts 폴더로 이동합니다.
npm install firebase-admin axios 명령어로 필요한 패키지를 설치합니다.
다운로드한 Firebase 서비스 계정 키 파일의 이름을 serviceAccountKey.json으로 변경하여 standalone_scripts 폴더에 위치시킵니다.
updateFirebaseWeather.js 파일 내의 기상청 API 키(KMA_API_KEY)를 유효한 키로 교체합니다.
산불 위치 크롤러 (selenium_fire_crawler.py):

standalone_scripts 폴더로 이동합니다.
pip install selenium pillow apscheduler 명령어로 필요한 패키지를 설치합니다.
selenium_fire_crawler.py 파일 내 driver_path 변수에 다운로드한 chromedriver.exe의 절대 경로를 설정합니다.
4. 시스템 실행
각 컴포넌트는 별도의 터미널에서 실행해야 합니다.

날씨 정보 수집기 실행:

Bash

cd standalone_scripts
node updateFirebaseWeather.js
산불 위치 크롤러 실행:

Bash

cd standalone_scripts
python selenium_fire_crawler.py
백엔드 서버 실행:

Bash

cd backend
node apiServer.js
(서버가 http://localhost:3001 에서 실행됩니다.)

프론트엔드 개발 서버 실행:

Bash

cd firefighter
npm start
(웹 브라우저에서 http://localhost:3000 로 접속하여 확인합니다.)

배포 시: firefighter 폴더에서 npm run build를 실행한 후, 백엔드 서버(apiServer.js)만 실행하면 서버가 빌드된 React 앱과 API를 함께 서비스합니다.

7. API 엔드포인트 명세
POST /api/predict-fire-spread

설명: 특정 지점의 산불 확산을 시뮬레이션합니다.
Request Body: { "ignition_id": <number> }
Response Body (Success):
JSON

{
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [...] },
      "properties": { "id": 123, "ignitionTime": 0, "burnoutTime": 3600 }
    },
    ...
  ],
  "timeBoundaries": [
    {
      "time": 600,
      "polygon": { "type": "Polygon", "coordinates": [[...]] }
    },
    ...
  ]
}
Response Body (Error): { "error": "에러 메시지" }
GET /api/mapped-grid-data

설명: 지도에 표시할 전체 격자점의 위치 데이터를 GeoJSON 형식으로 반환합니다.
GET /api/grid-with-fuel-info

설명: 각 격자점의 위치와 연료 등급 점수를 GeoJSON 형식으로 반환합니다.
