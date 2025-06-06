const turf = require('@turf/turf');

exports.isPointInArea = (point, polygon) => {
  return turf.booleanPointInPolygon(
    turf.point(point),
    turf.polygon(polygon.coordinates)
  );
};
