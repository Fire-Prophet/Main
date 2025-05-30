/**
 * 재난 문자 발송 시뮬레이션
 */
function sendEmergencyAlert(region, dangerLevel) {
    const msg = `📢 [경보] ${region} 지역 산불 위험 수준 ${dangerLevel}!`;
    console.log(msg);
    return msg;
}

module.exports = sendEmergencyAlert;
""",

    "09_coordsValidator.js": """\
/**
 * 위도/경도 유효성 검사
 */
function isValidCoordinate(x, y) {
    return x >= 124 && x <= 132 && y >= 33 && y <= 43;
}

module.exports = isValidCoordinate;
""",

    "10_exportGeoJSON.js": """\
/**
 * GeoJSON 포맷으로 데이터 변환
 */
function exportGeoJSON(points) {
    return {
        type: 'FeatureCollection',
        features: points.map(p => ({
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [p.x, p.y] },
            properties: { id: p.id, risk: p.risk }
        }))
    };
}