const db = require('./db');

exports.insertPrediction = async ({ region, temp, humidity, wind, risk }) => {
  await db.execute(
    'INSERT INTO predictions (region, temp, humidity, wind, risk_level) VALUES (?, ?, ?, ?, ?)',
    [region, temp, humidity, wind, risk]
  );
};
