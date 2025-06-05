const db = require('./db');

exports.getRecentPredictions = async () => {
  const [rows] = await db.query('SELECT * FROM predictions ORDER BY predicted_at DESC LIMIT 20');
  return rows;
};
