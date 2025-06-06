const proj4 = require('proj4');

exports.reprojectCoords = (coords, from, to) => {
  return coords.map(([x, y]) => proj4(from, to, [x, y]));
};
