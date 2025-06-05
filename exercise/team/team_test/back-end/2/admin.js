const express = require('express');
const router = express.Router();
const roleCheck = require('../middleware/roleCheck');

router.get('/dashboard', roleCheck, (req, res) => {
  res.json({ users: 12, predictions: 234, active: true });
});

module.exports = router;
