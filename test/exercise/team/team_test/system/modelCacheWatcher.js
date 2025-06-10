const fs = require('fs');
const { loadModel } = require('./modelStore');

exports.watchModelFile = (path) => {
  fs.watchFile(path, () => {
    console.log('🔁 모델 변경 감지 – 재로딩');
    loadModel(true); // 강제 재로딩
  });
};
