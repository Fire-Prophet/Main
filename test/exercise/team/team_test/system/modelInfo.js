const express = require('express');
const router = express.Router();
const fs = require('fs');

router.get('/', (req, res) => {
  const stats = fs.statSync('models/fire_model_latest.pkl');
  res.json({
    size: stats.size,
    updatedAt: stats.mtime,
    name: 'fire_model_latest.pkl'
  });
});

module.exports = router;
