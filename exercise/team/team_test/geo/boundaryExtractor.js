const turf = require('@turf/turf');

exports.extractBoundaries = (geojson) => {
  return turf.polygonToLine(geojson);
};
