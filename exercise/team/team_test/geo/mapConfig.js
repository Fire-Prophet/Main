const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.json({
    center: [126.9, 37.5],
    zoom: 7,
    baseMap: 'vworld',
    legend: [
      { label: '낮음', color: '#4CAF50' },
      { label: '보통', color: '#FFC107' },
      { label: '높음', color: '#FF5722' },
      { label: '위험', color: '#B71C1C' }
    ]
  });
});

module.exports = router;
