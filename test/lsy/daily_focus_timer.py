import time

def timer(minutes):
    print(f"{minutes}분 집중 시작!")
    for i in range(minutes * 60, 0, -1):
        mins, secs = divmod(i, 60)
        print(f"{mins:02d}:{secs:02d}", end='\r')
        time.sleep(1)
    print("집중 시간 끝! 🔔")

timer(1)  # 테스트용 1분
