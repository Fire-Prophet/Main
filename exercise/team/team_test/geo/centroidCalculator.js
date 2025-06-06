const turf = require('@turf/turf');

exports.calculateCentroid = (polygon) => {
  return turf.centroid(polygon).geometry.coordinates;
};
