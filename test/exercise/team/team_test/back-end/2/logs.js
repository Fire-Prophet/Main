const express = require('express');
const router = express.Router();
const { readLogs } = require('../controllers/logsController');

router.get('/', readLogs);

module.exports = router;
