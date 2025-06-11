const { exec } = require('child_process');

exports.retrainModel = (req, res) => {
  exec('python3 ai/trainModel.py', (err, stdout, stderr) => {
    if (err) return res.status(500).json({ error: stderr });
    res.json({ message: '재학습 완료', log: stdout });
  });
};
