import os

# 새 디렉토리 경로
dummy_code_path = "/mnt/data/fire_dummy_modules"

# 예시 더미 코드 10개 (50줄 내외로 구성)
dummy_files = {
    "01_weatherFetcher.js": """\
/**
 * 산불 예측용 기상 데이터 가져오기 모듈
 */
async function fetchWeatherData(region) {
    // 더미 함수: 실제로는 공공 API 또는 센서에서 받아옴
    return {
        temperature: 23.5,
        humidity: 42,
        windSpeed: 3.6,
        windDirection: 110
    };
}

module.exports = fetchWeatherData;
""",

    "02_fireRiskCalculator.js": """\