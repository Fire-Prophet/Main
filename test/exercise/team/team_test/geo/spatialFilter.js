const turf = require('@turf/turf');

exports.filterByBoundsAndRisk = (features, bbox, minRisk = 2) => {
  const boxPoly = turf.bboxPolygon(bbox);
  return features.filter(f => 
    turf.booleanIntersects(f, boxPoly) &&
    f.properties.risk >= minRisk
  );
};
