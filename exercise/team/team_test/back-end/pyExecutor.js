const { spawn } = require('child_process');

exports.runPythonModel = (temp, humidity, wind) => {
  return new Promise((resolve, reject) => {
    const py = spawn('python', ['fire_predictor.py', temp, humidity, wind]);

    let result = '';
    py.stdout.on('data', (data) => result += data);
    py.stderr.on('data', (err) => reject(err));
    py.on('close', () => resolve(result));
  });
};
