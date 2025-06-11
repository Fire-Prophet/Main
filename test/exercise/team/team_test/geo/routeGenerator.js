const turf = require('@turf/turf');

exports.generateLineRoute = (start, end) => {
  return turf.lineString([start, end], { purpose: 'evacuation' });
};
