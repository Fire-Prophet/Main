const fs = require('fs');
const path = require('path');

exports.handleUpload = (req, res) => {
  const filePath = path.join(__dirname, '..', req.file.path);
  console.log('📦 CSV uploaded:', filePath);
  res.json({ message: '업로드 완료', filename: req.file.filename });
};
