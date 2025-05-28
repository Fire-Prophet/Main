export function getAverageRisk(data) {
  const levels = { 낮음: 1, 보통: 2, 높음: 3, 위험: 4 };
  const sum = data.reduce((acc, d) => acc + (levels[d.risk] || 0), 0);
  const avg = sum / data.length;
  return Object.entries(levels).find(([_, val]) => val >= avg)?.[0] || '정보 부족';
}
