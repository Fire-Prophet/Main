const exec = require('child_process').exec;

exports.convertGeoJSONToMVT = (filePath) => {
  exec(`tippecanoe -o tiles.mbtiles ${filePath}`, (err, stdout) => {
    if (err) console.error('MVT 변환 실패');
  });
};
