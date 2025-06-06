const express = require('express');
const router = express.Router();
const { checkDanger } = require('../controllers/alertController');

router.post('/', checkDanger);

module.exports = router;
