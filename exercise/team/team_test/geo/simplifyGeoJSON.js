const turf = require('@turf/turf');

exports.simplify = (geojson, tolerance = 0.01) => {
  return turf.simplify(geojson, { tolerance, highQuality: false });
};
