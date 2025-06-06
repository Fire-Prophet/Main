const turf = require('@turf/turf');

exports.mergePolygons = (features) => {
  const unioned = features.reduce((acc, curr) => turf.union(acc, curr));
  return turf.featureCollection([unioned]);
};
