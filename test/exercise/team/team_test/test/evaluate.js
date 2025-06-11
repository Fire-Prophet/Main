const express = require('express');
const router = express.Router();
const { evaluateModel } = require('../../controllers/ai/evaluateController');

router.get('/', evaluateModel);

module.exports = router;
