const { runPythonModel } = require('../utils/pyExecutor');

exports.predictFireRisk = async (req, res) => {
  const { temp, humidity, wind } = req.body;
  try {
    const result = await runPythonModel(temp, humidity, wind);
    res.json({ risk: result.trim() });
  } catch (err) {
    res.status(500).json({ error: '예측 실패', detail: err.message });
  }
};
