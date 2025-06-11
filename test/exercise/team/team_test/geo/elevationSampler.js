const GeoTIFF = require('geotiff');

exports.sampleElevation = async (filePath, lon, lat) => {
  const tiff = await GeoTIFF.fromFile(filePath);
  const image = await tiff.getImage();
  const value = await image.readRasters({ window: [lon, lat, lon + 1, lat + 1] });
  return value[0][0];
};
