👨‍🚒 FireFighter: 산불 확산 예측 및 실시간 모니터링 시스템
본 프로젝트는 실시간 산불 정보 연동 기능과, 사용자가 지정한 발화점을 기준으로 산불의 확산 경로 및 피해 범위를 시각적으로 예측하는 풀스택 웹 애플리케이션입니다.

Frontend: React, OpenLayers

Backend: Node.js, Express

Crawler: Python, Selenium, Pillow, APScheduler

Database: MySQL, Firebase Realtime Database

Infra: DDNS, Port Forwarding

📝 목차
프로젝트 구조

사전 준비 사항

설정 방법

실행 방법

주요 기능

📁 프로젝트 구조
프로젝트는 backend, firefighter(프론트엔드), crawl_map(크롤러)의 세 가지 주요 디렉토리와 데이터 공유를 위한 shared_data 디렉토리로 구성됩니다.

/Project/
├── backend/                  # Node.js 백엔드 서버
│   ├── config/
│   ├── routes/
│   ├── services/
│   ├── apiServer.js
│   └── ...
│
├── firefighter/              # React 프론트엔드 앱
│   ├── public/
│   └── src/
│       ├── components/
│       │   └── VWorldMap.js
│       └── ...
│
├── crawl_map/                # Python 크롤러
│   └── selenium_fire_crawler.py
│
└── shared_data/              # 크롤러와 백엔드 간 데이터 공유 폴더
    └── fire_markers.json     # (크롤러 실행 시 자동 생성됨)

⚙️ 사전 준비 사항
애플리케이션을 실행하기 전에 다음 환경이 준비되어야 합니다.

Node.js: v18.x 이상 권장

Python: 3.x 버전

MySQL: 실행 중인 MySQL 데이터베이스 인스턴스

Google Chrome 및 ChromeDriver: Selenium이 사용할 브라우저와 드라이버

Firebase 프로젝트 (시뮬레이션 기능에 필요):

Firebase Realtime Database 활성화

서비스 계정 키(serviceAccountKey.json) 파일

🔥 설정 방법
각 파트를 순서대로 설정합니다.

1. Crawler (Python) 설정
디렉토리 이동: 터미널에서 crawl_map 디렉토리로 이동합니다.

cd crawl_map

의존성 설치:

pip install selenium pillow apscheduler

ChromeDriver 경로 수정: selenium_fire_crawler.py 파일을 열어, setup_driver 함수 내의 driver_path 변수에 본인의 chromedriver.exe 파일 절대 경로를 정확하게 입력합니다.

2. Backend (Node.js) 설정
디렉토리 이동 및 의존성 설치:

cd ../backend
npm install

Firebase 서비스 계정 키 설정 (선택 사항): 시뮬레이션 기능을 사용하려면, Firebase 콘솔에서 다운로드한 serviceAccountKey.json 파일을 backend 폴더 내에 위치시킵니다.

환경변수 파일(.env) 생성: backend 폴더 내에 .env 파일을 생성하고, 아래 내용을 본인의 MySQL 데이터베이스 정보에 맞게 수정합니다.

# MySQL DB 연결 정보
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=your_database

3. Frontend (React) 설정
디렉토리 이동 및 의존성 설치:

cd ../firefighter
npm install

🚀 실행 방법
총 3개의 터미널을 사용하여 각 파트를 개별적으로 실행합니다.

Crawler 실행 (1번 터미널): 가장 먼저 실행하고, 자동 업데이트를 위해 계속 켜두어야 합니다.

# /Project/crawl_map/ 경로에서
python selenium_fire_crawler.py

Backend 실행 (2번 터미널):

# /Project/backend/ 경로에서
node apiServer.js

Frontend 실행 (3번 터미널):

# /Project/firefighter/ 경로에서
npm start

실행 후, 웹 브라우저에서 http://localhost:3000 주소로 접속하면 애플리케이션을 확인할 수 있습니다.

✨ 주요 기능
실시간 산불 모니터링: Python 크롤러가 30분마다 산림청 사이트의 산불 정보를 분석하여 JSON 파일로 저장합니다. 프론트엔드는 이 데이터를 1분마다 새로고침하여, 지도 위에 현재 발생한 산불의 위치와 상태를 색상별 사각형 마커로 표시합니다.

동적 확산 시뮬레이션: 사용자가 지도 위의 격자점을 발화점으로 지정하면, 백엔드에서 물리 모델(연료량, 경사도, 습도, 바람 등)을 기반으로 산불 확산 결과를 계산합니다.

시간 제어 시각화: 시뮬레이션 결과는 시간 경과에 따른 연소(빨강), 확산 예상(노랑), 연소 완료(검정) 상태로 지도에 동적으로 표시되며, 사용자는 슬라이더를 통해 원하는 시간대의 결과를 확인할 수 있습니다.

지도 기반 인터페이스: OpenLayers를 사용하여 VWorld 지도를 표시하며, 다양한 데이터 레이어(격자, 관측소, 예측 결과)의 가시성을 제어하고 범례를 통해 각 색상의 의미를 확인할 수 있습니다.
