const express = require('express');
const router = express.Router();
const { getVersion } = require('../controllers/versionController');

router.get('/', getVersion);

module.exports = router;
