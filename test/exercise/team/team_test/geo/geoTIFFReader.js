const fs = require('fs');
const parse = require('geotiff');

exports.readGeoTIFFMeta = async (path) => {
  const buffer = fs.readFileSync(path);
  const tiff = await parse.fromArrayBuffer(buffer.buffer);
  const image = await tiff.getImage();
  return {
    width: image.getWidth(),
    height: image.getHeight(),
    bbox: image.getBoundingBox()
  };
};
