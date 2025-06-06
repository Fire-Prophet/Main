const turf = require('@turf/turf');

exports.aggregateRisk = (points, zones) => {
  return zones.features.map(zone => {
    const pts = points.features.filter(p => turf.booleanPointInPolygon(p, zone));
    const avg = pts.length ? pts.reduce((sum, p) => sum + p.properties.risk, 0) / pts.length : 0;
    return { ...zone.properties, avgRisk: avg };
  });
};
