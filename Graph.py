import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os # 운영체제 관련 모듈 추가

# --- 1. 설정 값 ---
# Firebase 서비스 계정 키 파일의 전체 경로를 정확하게 입력해주세요.
# 예: "C:/Users/YourUsername/path/to/your-service-account-key.json"
FIREBASE_CERT_PATH = "C:/Users/yangg/Desktop/tttest/abc/ljg20-5b27b-firebase-adminsdk-fbsvc-ccddd89158.json"
FIREBASE_DATABASE_URL = "https://ljg20-5b27b-default-rtdb.firebaseio.com/"
LOCATION_PATH = "weather_data/asan"  # Firebase에서 데이터가 저장된 기본 경로 (아산 지역)

# --- 2. Firebase 초기화 함수 ---
def initialize_firebase():
    """Firebase Admin SDK를 초기화합니다."""
    try:
        if not firebase_admin._apps:  # 앱이 이미 초기화되지 않았는지 확인
            if not os.path.exists(FIREBASE_CERT_PATH):
                print(f"❌ Firebase 인증서 파일을 찾을 수 없습니다: {FIREBASE_CERT_PATH}")
                print("   파일 경로가 정확한지, 파일이 해당 위치에 존재하는지 확인해주세요.")
                return False
            
            cred = credentials.Certificate(FIREBASE_CERT_PATH)
            firebase_admin.initialize_app(cred, {
                'databaseURL': FIREBASE_DATABASE_URL
            })
            print("✅ Firebase Admin SDK가 성공적으로 초기화되었습니다.")
        else:
            print("ℹ️ Firebase Admin SDK가 이미 초기화되어 있습니다.")
        return True
    except Exception as e:
        print(f"❌ Firebase Admin SDK 초기화 중 오류 발생: {e}")
        return False

# --- 3. Firebase에서 날씨 데이터 가져오기 ---
def fetch_weather_data_from_firebase(days_to_fetch=1):
    """
    Firebase Realtime Database에서 최근 지정된 일수만큼의 아산 날씨 데이터를 가져옵니다.
    데이터는 'weather_data/asan/YYYY-MM-DD/HH-MM-SS/' 구조로 저장되어 있다고 가정합니다.
    """
    all_records = []
    for i in range(days_to_fetch):
        target_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        ref_path = f'{LOCATION_PATH}/{target_date}'
        print(f"Firebase에서 데이터 경로 '{ref_path}'의 데이터를 가져옵니다.")
        
        try:
            ref = db.reference(ref_path)
            data_for_day = ref.get()

            if data_for_day:
                print(f"  {target_date}: {len(data_for_day)}개의 기록을 찾았습니다.")
                for time_str, data_points in data_for_day.items():
                    if isinstance(data_points, dict) and 'timestamp_iso' in data_points:
                        # timestamp_iso를 사용하여 정확한 시간 정보로 변환
                        record_time = datetime.fromisoformat(data_points['timestamp_iso'])
                        record = {
                            'timestamp': record_time,
                            'temperature': data_points.get('temperature_celsius'),
                            'humidity': data_points.get('humidity_percent'),
                            'precipitation': data_points.get('precipitation_mm'),
                            'wind_speed': data_points.get('wind_speed_mps')
                        }
                        all_records.append(record)
                    else:
                        print(f"    경고: {time_str}의 데이터 형식이 올바르지 않거나 'timestamp_iso'가 없습니다. 건너<0xEB><0x9A><0x88>뜁니다: {data_points}")
            else:
                print(f"  {target_date}: 경로 '{ref_path}'에서 데이터를 찾을 수 없습니다.")
        except Exception as e:
            print(f"Firebase에서 '{ref_path}' 경로의 데이터를 가져오는 중 오류 발생: {e}")
            continue # 특정 날짜에 오류 발생 시 다음 날짜로 넘어감
            
    if not all_records:
        print("Firebase에서 가져올 수 있는 날씨 데이터가 없습니다.")
        return pd.DataFrame()

    df = pd.DataFrame(all_records)
    df = df.set_index('timestamp')
    df = df.sort_index() # 시간순으로 정렬

    # 숫자형으로 변환 (이미 float/int일 수 있으나, 안전하게 처리)
    for col in ['temperature', 'humidity', 'precipitation', 'wind_speed']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce') # 변환 불가능한 값은 NaT/NaN으로 처리

    return df

# --- 4. 데이터 시각화 함수 ---
def visualize_weather_trends(df, location_name="아산"):
    """
    Pandas DataFrame의 날씨 데이터를 사용하여 추세 그래프를 그립니다.
    """
    if df.empty:
        print("시각화할 데이터가 없습니다.")
        return

    # 한글 폰트 설정 (Windows: Malgun Gothic, macOS: AppleGothic)
    # 시스템에 적절한 한글 폰트가 설치되어 있어야 합니다.
    try:
        plt.rcParams['font.family'] = 'Malgun Gothic' # Windows
        # plt.rcParams['font.family'] = 'AppleGothic' # macOS 사용자
    except RuntimeError:
        print("경고: 한글 폰트('Malgun Gothic' 또는 'AppleGothic')를 찾을 수 없습니다. 그래프의 글자가 깨질 수 있습니다.")
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 부호 깨짐 방지

    # 시각화할 데이터 항목 정의
    plot_items = {
        'temperature': {'label': '온도 (°C)', 'color': 'red'},
        'humidity': {'label': '습도 (%)', 'color': 'green'},
        'precipitation': {'label': '강수량 (mm)', 'color': 'blue'},
        'wind_speed': {'label': '풍속 (m/s)', 'color': 'purple'}
    }

    # DataFrame에 존재하는 컬럼만 필터링
    available_plots = {key: info for key, info in plot_items.items() if key in df.columns and not df[key].isnull().all()}

    if not available_plots:
        print("시각화할 유효한 데이터 컬럼(온도, 습도, 강수량, 풍속)이 없습니다.")
        return

    num_plots = len(available_plots)
    fig, axes = plt.subplots(nrows=num_plots, ncols=1, figsize=(14, 4 * num_plots), sharex=True)
    
    if num_plots == 1: # 서브플롯이 하나일 경우 axes가 배열이 아님
        axes = [axes]

    plot_idx = 0
    for key, item_info in available_plots.items():
        ax = axes[plot_idx]
        sns.lineplot(ax=ax, x=df.index, y=key, data=df, marker='o', label=item_info['label'], color=item_info['color'])
        ax.set_ylabel(item_info['label'])
        ax.set_title(f'{location_name} 최근 {item_info["label"].split(" ")[0]} 변화') # 예: "아산 최근 온도 변화"
        ax.grid(True)
        ax.legend()
        plot_idx += 1

    # X축 레이블 설정
    if df.index.name or isinstance(df.index, pd.DatetimeIndex):
        axes[-1].set_xlabel('시간')
    else:
        axes[-1].set_xlabel('데이터 포인트 인덱스')
    
    fig.autofmt_xdate() # X축 날짜/시간 레이블 자동 포맷
    plt.suptitle(f'{location_name} 최근 날씨 동향', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96]) # suptitle과 겹치지 않도록 조정
    plt.show()

# --- 5. 메인 실행 부분 ---
if __name__ == '__main__':
    print("날씨 데이터 시각화 프로그램을 시작합니다...")

    if initialize_firebase():
        # 최근 1일치 데이터를 가져와서 시각화 (원하는 일수로 변경 가능, 예: 7일)
        weather_df = fetch_weather_data_from_firebase(days_to_fetch=1)

        if not weather_df.empty:
            print("\n--- 불러온 날씨 데이터 (일부) ---")
            print(weather_df.head()) # 처음 5개 데이터 출력
            print("...")
            print(weather_df.tail()) # 마지막 5개 데이터 출력

            visualize_weather_trends(weather_df, location_name="아산")
        else:
            print("표시할 데이터가 없습니다. Firebase에 데이터가 올바르게 저장되었는지, 경로가 맞는지 확인해주세요.")
    else:
        print("Firebase 초기화 실패. 프로그램을 종료합니다.")

    print("시각화 프로그램이 종료되었습니다.")
