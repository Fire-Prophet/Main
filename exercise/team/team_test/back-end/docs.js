const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.json({
    routes: [
      { path: '/predict', method: 'POST', description: '산불 위험도 예측' },
      { path: '/upload', method: 'POST', description: 'CSV 업로드' }
    ]
  });
});

module.exports = router;
