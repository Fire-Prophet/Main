module.exports = renderFireRiskLayer;
""",

    "05_simulateIgnition.js": """\
/**
 * 임의 발화 지점 지정 및 주변 위험도 변화 시뮬레이션
 */
function simulateIgnition(centerX, centerY, data) {
    return data.map(pt => {
        const dx = pt.x - centerX;
        const dy = pt.y - centerY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        pt.risk += dist < 0.05 ? 3 : dist < 0.1 ? 1 : 0;
        return pt;
    });
}