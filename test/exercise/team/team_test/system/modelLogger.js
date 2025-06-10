const fs = require('fs');

exports.logPrediction = (input, output) => {
  const log = {
    time: new Date().toISOString(),
    input,
    output
  };
  fs.appendFileSync('logs/predict.log', JSON.stringify(log) + '\n');
};
