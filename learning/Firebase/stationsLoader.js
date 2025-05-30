function loadMountainStations(filePath) {
    try {
        const stationsModule = require(filePath);
        const mountainStationsData = stationsModule.mountainStationsData || stationsModule;

        if (!Array.isArray(mountainStationsData)) {
            throw new Error("mountainStationsData가 배열이 아닙니다.");
        }

        console.log(`총 ${mountainStationsData.length}개의 관측소 데이터 로드됨.`);
        return mountainStationsData;
    } catch (error) {
        console.error(`관측소 데이터 로드 실패: ${error.message}`);
        process.exit(1);
    }
}

module.exports = loadMountainStations;
