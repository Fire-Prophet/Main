module.exports = readSensorData;
""",

    "04_fireMapRenderer.js": """\
/**
 * 지도 상에 위험도 레이어 렌더링 (가상)
 */
function renderFireRiskLayer(points) {
    points.forEach(pt => {
        console.log(`🔥 위험도 ${pt.risk} - 위치: (${pt.x}, ${pt.y})`);
    });
}