const fs = require('fs');

module.exports = function logToFile(message) {
  const logLine = `[${new Date().toISOString()}] ${message}\n`;
  fs.appendFile('server.log', logLine, (err) => {
    if (err) console.error('로그 저장 실패:', err.message);
  });
};
