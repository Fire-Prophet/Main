const express = require('express');
const router = express.Router();
const { explain } = require('../../controllers/ai/explainController');

router.post('/', explain);

module.exports = router;
