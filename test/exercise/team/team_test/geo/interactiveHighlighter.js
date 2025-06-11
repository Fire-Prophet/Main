exports.buildHighlightFeature = (feature) => {
  return {
    ...feature,
    properties: {
      ...feature.properties,
      _highlighted: true
    }
  };
};
