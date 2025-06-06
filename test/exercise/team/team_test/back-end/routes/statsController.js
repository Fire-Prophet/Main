exports.getStats = (req, res) => {
  const mockData = ['낮음', '낮음', '보통', '높음', '위험', '보통'];
  const stats = {};
  mockData.forEach(r => stats[r] = (stats[r] || 0) + 1);
  res.json(stats);
};
