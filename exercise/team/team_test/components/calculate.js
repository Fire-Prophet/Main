export function calculateFireRisk({ temp, humidity, wind }) {
  if (temp > 30 && humidity < 30 && wind > 5) return '위험';
  if (temp > 25 && humidity < 40) return '높음';
  if (temp > 20 && humidity < 50) return '보통';
  return '낮음';
}
