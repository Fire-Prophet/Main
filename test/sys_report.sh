#!/bin/bash

# sys_report.sh - 간단한 시스템 정보 보고서 스크립트

# 스크립트 시작 시 현재 시간 기록
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
REPORT_FILE="system_report_$(date +"%Y%m%d_%H%M%S").txt"

echo "--- 시스템 정보 보고서 시작: $START_TIME ---" | tee "$REPORT_FILE"
echo "보고서 파일: $REPORT_FILE" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 1. 호스트 이름 정보
echo "## 1. 호스트 이름" | tee -a "$REPORT_FILE"
hostname | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 2. 운영체제 정보
echo "## 2. 운영체제 정보" | tee -a "$REPORT_FILE"
uname -a | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 3. CPU 정보
echo "## 3. CPU 정보" | tee -a "$REPORT_FILE"
# /proc/cpuinfo에서 모델 이름만 추출
grep -m 1 "model name" /proc/cpuinfo | awk -F: '{print $2}' | tee -a "$REPORT_FILE"
# 코어 수 확인 (CPU에 따라 다를 수 있음)
grep -c ^processor /proc/cpuinfo | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 4. 메모리 정보
echo "## 4. 메모리 정보 (MB)" | tee -a "$REPORT_FILE"
# total, used, free 메모리 정보 (MB 단위로 출력)
free -h | head -n 2 | tail -n 1 | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 5. 디스크 사용량 (루트 파티션)
echo "## 5. 디스크 사용량 (루트 파티션)" | tee -a "$REPORT_FILE"
df -h / | tail -n 1 | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 6. 네트워크 인터페이스 정보 (IP 주소만)
echo "## 6. 네트워크 인터페이스 (IP 주소)" | tee -a "$REPORT_FILE"
# ip -4 addr show는 IPv4 주소만 표시하고, grep과 awk로 필요한 정보만 필터링
ip -4 addr show | grep -oP 'inet \K[\d.]+' | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 7. 현재 로그인 사용자
echo "## 7. 현재 로그인 사용자" | tee -a "$REPORT_FILE"
who | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 8. 실행 중인 프로세스 수 (간단한 예시)
echo "## 8. 실행 중인 프로세스 수" | tee -a "$REPORT_FILE"
ps aux | wc -l | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 스크립트 종료 시 현재 시간 기록
END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "--- 시스템 정보 보고서 종료: $END_TIME ---" | tee -a "$REPORT_FILE"
echo "보고서 작성이 완료되었습니다: $REPORT_FILE"
echo "생성된 보고서 파일 내용을 보려면 'cat $REPORT_FILE'를 실행하세요."
