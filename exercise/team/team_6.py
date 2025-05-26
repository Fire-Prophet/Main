module.exports = simulateIgnition;
""",

    "06_dataLogger.js": """\
/**
 * 로그 기록 및 저장용 유틸
 */
const fs = require('fs');
function logToFile(filename, content) {
    fs.appendFileSync(filename, `[${new Date().toISOString()}] ${content}\\n`);
}

module.exports = logToFile;
""",

    "07_dummyDb.js": """\