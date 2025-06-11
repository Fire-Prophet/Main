const turf = require('@turf/turf');

exports.createBuffer = (point, radiusKm) => {
  return turf.buffer(turf.point(point), radiusKm, { units: 'kilometers' });
};
