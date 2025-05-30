import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import mysql.connector
import random
import time
import datetime
import os                   # os 모듈 임포트
from dotenv import load_dotenv # dotenv 임포트

# --- .env 파일 로드 ---
load_dotenv() # 스크립트 시작 시 .env 파일 로드
# --------------------

# --- .env에서 설정값 가져오기 ---
MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER'), # 필수값이므로 기본값 없음
    'password': os.getenv('DB_PASSWORD'), # 필수값이므로 기본값 없음
    'database': os.getenv('DB_DATABASE') # 필수값이므로 기본값 없음
}
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH')
FIREBASE_DB_URL = os.getenv('FIREBASE_DB_URL')
UPDATE_INTERVAL_SECONDS = int(os.getenv('UPDATE_INTERVAL_SECONDS', 10)) # 기본값 10초
REFRESH_MYSQL_INTERVAL_SECONDS = int(os.getenv('REFRESH_MYSQL_INTERVAL_SECONDS', 60)) # 기본값 60초
# -----------------------------

# --- 필수 설정값 확인 ---
if not all([MYSQL_CONFIG['user'], MYSQL_CONFIG['password'], MYSQL_CONFIG['database'], FIREBASE_CRED_PATH, FIREBASE_DB_URL]):
    print("오류: .env 파일에 필수 설정(DB_USER, DB_PASSWORD, DB_DATABASE, FIREBASE_CRED_PATH, FIREBASE_DB_URL)이 누락되었습니다.")
    exit(1) # 필수값이 없으면 종료
# -------------------------


def get_parking_spaces_from_mysql():
    """MySQL에서 LotID와 SpaceID 목록을 가져옵니다."""
    spaces = []
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT LotID, SpaceID FROM ParkingSpaces")
        rows = cursor.fetchall()
        for row in rows:
            spaces.append({'LotID': row[0], 'SpaceID': row[1]})
    except mysql.connector.Error as err:
        print(f"MySQL 연결 오류: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return spaces

def simulate_parking_status():
    """Firebase에 실시간 주차 상태를 업데이트합니다."""
    # Firebase 초기화 (한 번만 실행)
    try:
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_DB_URL
        })
        print("Firebase가 성공적으로 초기화되었습니다.")
    except Exception as e:
        if "already exists" not in str(e):
            print(f"Firebase 초기화 오류: {e}")
            return
        else:
            print("Firebase가 이미 초기화되어 있습니다.")

    root_ref = db.reference('/ParkingStatus')
    print("시뮬레이션을 시작합니다. Ctrl+C를 눌러 중지하세요.")

    last_mysql_refresh_time = 0
    all_spaces = []

    while True:
        try:
            current_time = time.time()

            # MySQL 목록 새로고침
            if not all_spaces or (current_time - last_mysql_refresh_time) > REFRESH_MYSQL_INTERVAL_SECONDS:
                print(f"[{datetime.datetime.now()}] MySQL 주차장 목록을 새로고침합니다...")
                all_spaces = get_parking_spaces_from_mysql()
                last_mysql_refresh_time = current_time
                if not all_spaces:
                    print("  >> 주차장 정보 없음. 60초 후 다시 시도합니다.")
                    time.sleep(60)
                    continue
                else:
                    print(f"  >> {len(all_spaces)}개의 주차면 정보를 로드했습니다.")

            updates = {}
            lot_available_counts = {}

            # 모든 주차면에 대해 랜덤 상태 생성
            for space in all_spaces:
                lot_id = f"LotID_{space['LotID']}"
                space_id = f"SpaceID_{space['SpaceID']}"
                status = random.choice(["available", "occupied"])
                timestamp = int(time.time() * 1000)

                updates[f'{lot_id}/Spaces/{space_id}/status'] = status
                updates[f'{lot_id}/Spaces/{space_id}/timestamp'] = timestamp

                if lot_id not in lot_available_counts:
                    lot_available_counts[lot_id] = 0
                if status == "available":
                    lot_available_counts[lot_id] += 1

            for lot_id, count in lot_available_counts.items():
                updates[f'{lot_id}/AvailableCount'] = count

            root_ref.update(updates)
            print(f"[{datetime.datetime.now()}] Firebase 업데이트 완료.")
            time.sleep(UPDATE_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n시뮬레이션을 중지합니다.")
            break
        except Exception as e:
            print(f"오류 발생: {e}. 10초 후 재시도합니다.")
            time.sleep(10)

if __name__ == "__main__":
    simulate_parking_status()
