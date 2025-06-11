const express = require('express');
const router = express.Router();
const { predict } = require('../../controllers/ai/predictController');

router.post('/', predict);

module.exports = router;
