const initializeFirebase = require('./firebase');
const fetchKmaWeatherData = require('./kmaApi');
const loadMountainStations = require('./stationsLoader');

const MOUNTAIN_STATIONS_PATH = './mountainStations.js';
const UPDATE_INTERVAL_MS = 60 * 60 * 1000; // 1시간

const db = initializeFirebase();
const mountainStationsData = loadMountainStations(MOUNTAIN_STATIONS_PATH);

async function updateAllStationsWeather() {
    console.log('[Firebase 업데이트] 주기적 날씨 정보 업데이트 작업을 시작합니다...');
    const now = new Date();
    now.setMinutes(0, 0, 0);

    const requestTm = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}${String(now.getHours()).padStart(2, '0')}00`;

    let successCount = 0;
    let errorCount = 0;

    for (const station of mountainStationsData) {
        const obsid = station.obsid;
        const weatherData = await fetchKmaWeatherData(obsid, requestTm);

        if (weatherData) {
            try {
                await db.ref(`weatherdata/${obsid}`).set(weatherData);
                successCount++;
            } catch (error) {
                console.error(`Firebase 업데이트 실패: ${error.message}`);
                errorCount++;
            }
        }
    }

    console.log(`업데이트 완료: 성공 ${successCount}건, 실패 ${errorCount}건`);
}

async function runUpdateCycle() {
    await updateAllStationsWeather();
}

setInterval(runUpdateCycle, UPDATE_INTERVAL_MS);
runUpdateCycle();
