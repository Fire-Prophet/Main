const parseCSV = require('../utils/parseCSV');

exports.analyzeUpload = async (req, res) => {
  try {
    const rows = await parseCSV(req.file.path);
    const count = rows.length;
    res.json({ message: '행 개수 분석 완료', count });
  } catch (e) {
    res.status(400).json({ error: 'CSV 파싱 실패' });
  }
};
