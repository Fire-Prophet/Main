const db = require('./db');

exports.getStats = async () => {
  const [rows] = await db.query(`
    SELECT region, risk_level, COUNT(*) AS count
    FROM predictions
    GROUP BY region, risk_level
  `);
  return rows;
};
