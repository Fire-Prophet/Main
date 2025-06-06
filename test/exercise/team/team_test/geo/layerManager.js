const layers = [];

exports.addLayer = (layer) => {
  layers.push(layer);
};

exports.getLayers = () => layers;
