exports.getStats = (req, res) => {
  // 예시 통계
  res.json({
    totalRegions: 21,
    avgRisk: '보통',
    topRiskAreas: ['청양', '속초', '양양']
  });
};
