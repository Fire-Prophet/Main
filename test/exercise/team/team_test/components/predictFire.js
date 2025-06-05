export function predictFireSpread(origin, windDir, terrain) {
  // 단순 논리 예시: 바람 방향으로 N km 확산
  const [x, y] = origin;
  const delta = windDir === 'E' ? [1, 0] : windDir === 'N' ? [0, -1] : [-1, 0];
  return Array.from({ length: 5 }, (_, i) => [x + delta[0] * i, y + delta[1] * i]);
}
