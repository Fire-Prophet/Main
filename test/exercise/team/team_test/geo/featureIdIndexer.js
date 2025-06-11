exports.assignIds = (geojson) => {
  geojson.features.forEach((f, i) => {
    f.properties.id = `F-${i + 1}`;
  });
  return geojson;
};
