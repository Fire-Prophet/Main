const express = require('express');
const router = express.Router();
const geoData = require('../data/mockGeoData.json');

router.get('/', (req, res) => {
  res.json(geoData);
});

module.exports = router;
