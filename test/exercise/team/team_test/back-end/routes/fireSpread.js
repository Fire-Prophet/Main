exports.simulateSpread = (origin, windDir) => {
  const [x, y] = origin;
  const dir = windDir === 'E' ? [1, 0] : windDir === 'N' ? [0, -1] : [-1, 0];
  return Array.from({ length: 5 }, (_, i) => [x + dir[0] * i, y + dir[1] * i]);
};
