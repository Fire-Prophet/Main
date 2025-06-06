const express = require('express');
const router = express.Router();
const { predictFireRisk } = require('../controllers/predictController');

router.post('/', predictFireRisk);

module.exports = router;
