const fs = require('fs');
const path = require('path');

exports.uploadModel = (req, res) => {
  const dest = path.join('models', 'fire_model_latest.pkl');
  fs.renameSync(req.file.path, dest);
  res.json({ message: '모델 업로드 및 적용 완료' });
};
