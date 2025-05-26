/**
 * 기상 정보와 연료 강도 기반 산불 위험도 계산
 */
function calculateFireRisk(humidity, windSpeed, fuelStrength) {
    let score = fuelStrength || 1;

    if (humidity < 30) score += 3;
    else if (humidity < 50) score += 1;
    else score -= 1;

    if (windSpeed > 4) score += 2;
    else if (windSpeed > 2) score += 1;

    return Math.min(10, Math.max(0, score));
}
