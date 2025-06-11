const turf = require('@turf/turf');

exports.calculateArea = (polygon) => {
  const area = turf.area(polygon); // m²
  return (area / 1000000).toFixed(2); // km²로 환산
};
