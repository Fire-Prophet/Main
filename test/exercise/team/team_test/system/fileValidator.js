const fs = require('fs');

exports.validateModelFile = (filePath) => {
  const valid = fs.existsSync(filePath) && filePath.endsWith('.pkl');
  if (!valid) throw new Error('모델 파일이 유효하지 않습니다.');
};
