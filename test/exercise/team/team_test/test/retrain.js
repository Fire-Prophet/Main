const express = require('express');
const router = express.Router();
const { retrainModel } = require('../../controllers/ai/retrainController');

router.post('/', retrainModel);

module.exports = router;
