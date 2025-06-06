exports.validateGeoJSON = (data) => {
  return (
    data &&
    data.type === 'FeatureCollection' &&
    Array.isArray(data.features)
  );
};
