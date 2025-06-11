let layerStates = {};

exports.toggleLayer = (layerName) => {
  layerStates[layerName] = !layerStates[layerName];
};

exports.getLayerState = (layerName) => !!layerStates[layerName];
