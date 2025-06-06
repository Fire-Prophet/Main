const express = require('express');
const router = express.Router();
const { predictTomorrow } = require('../controllers/forecastController');

router.post('/', predictTomorrow);

module.exports = router;
