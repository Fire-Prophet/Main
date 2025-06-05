const express = require('express');
const router = express.Router();
const { getStats } = require('../controllers/geoDashboard');

router.get('/', getStats);

module.exports = router;
