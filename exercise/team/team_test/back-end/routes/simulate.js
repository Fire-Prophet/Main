const express = require('express');
const router = express.Router();
const { simulateSpread } = require('../utils/fireSpread');

router.post('/', (req, res) => {
  const { origin, windDir } = req.body;
  const path = simulateSpread(origin, windDir);
  res.json({ spreadPath: path });
});

module.exports = router;
