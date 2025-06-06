const turf = require('@turf/turf');

exports.clipGeoJSON = (geojson, bbox) => {
  const bboxPoly = turf.bboxPolygon(bbox); // [minX, minY, maxX, maxY]
  return turf.intersect(geojson, bboxPoly);
};
