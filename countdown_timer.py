# countdown_timer.py
import time
import sys # stdout.write, stdout.flush 용

def countdown(total_seconds):
    """지정된 시간(초) 동안 카운트다운을 실행합니다."""
    if total_seconds <= 0:
        print("카운트다운 시간은 0보다 커야 합니다.")
        return

    print("카운트다운 시작!")
    
    while total_seconds > 0:
        # 분과 초 계산
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        # 시간 표시 형식 (MM:SS)
        time_display = f"{minutes:02d}:{seconds:02d}"
        
        # 같은 줄에 덮어쓰기 위해 \r 사용
        # sys.stdout.write 와 sys.stdout.flush() 는 IDLE 환경에서는 잘 동작하지 않을 수 있음
        # 터미널/콘솔 환경에서 실행 권장
        sys.stdout.write(f"\r남은 시간: {time_display}  ") # 뒤에 공백 추가는 이전 글자 덮어쓰기 위함
        sys.stdout.flush()
        
        time.sleep(1) # 1초 대기
        total_seconds -= 1
        
    sys.stdout.write("\r카운트다운 종료!              \n") # 마지막 메시지 및 줄바꿈
    sys.stdout.flush()
    # 알림음 (선택적) - 시스템에 따라 동작 안할 수 있음
    # print('\a') # Bell character

def main():
    """카운트다운 타이머 메인 함수"""
    print("카운트다운 타이머입니다.")
    
    while True:
        try:
            minutes_input = int(input("카운트다운 할 시간을 분 단위로 입력하세요: "))
            seconds_input = int(input("카운트다운 할 시간을 초 단위로 입력하세요 (0-59): "))
            
            if minutes_input < 0 or seconds_input < 0 or seconds_input >= 60:
                print("잘못된 시간 입력입니다. 분은 0 이상, 초는 0-59 사이로 입력하세요.")
                continue
            
            total_seconds = minutes_input * 60 + seconds_input
            if total_seconds == 0:
                print("총 카운트다운 시간은 0초보다 커야 합니다.")
                continue
            break
        except ValueError:
            print("숫자를 입력해주세요.")
            
    countdown(total_seconds)

    # 추가 기능: 카운트다운 후 특정 작업 실행 등
    print("타이머가 완료되었습니다.")

if __name__ == "__main__":
    main()
