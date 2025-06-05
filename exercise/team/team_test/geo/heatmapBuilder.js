exports.buildHeatmapData = (pointList) => {
  return pointList.map(p => ({
    lat: p[1],
    lon: p[0],
    weight: p.riskLevel
  }));
};
