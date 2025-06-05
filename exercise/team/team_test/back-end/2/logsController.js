const fs = require('fs');
const path = require('path');

exports.readLogs = (req, res) => {
  const file = path.join(__dirname, '../server.log');
  fs.readFile(file, 'utf8', (err, data) => {
    if (err) return res.status(500).send('로그 파일 없음');
    res.send(`<pre>${data}</pre>`);
  });
};
