const supercluster = require('supercluster');

exports.clusterPoints = (pointsGeoJSON, zoom = 10) => {
  const index = new supercluster({ radius: 40 });
  index.load(pointsGeoJSON.features);
  return index.getClusters([-180, -85, 180, 85], zoom);
};
