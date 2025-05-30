module.exports = calculateFireRisk;
""",

    "03_mockSensorReader.js": """\
/**
 * 더미 센서 데이터 읽기
 */
function readSensorData(sensorId) {
    const sensors = {
        'S001': { coord: [127.1, 36.7], fuel: 4.5 },
        'S002': { coord: [127.2, 36.8], fuel: 3.8 },
        'S003': { coord: [127.3, 36.75], fuel: 2.9 }
    };
    return sensors[sensorId] || null;
}