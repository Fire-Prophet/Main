const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.json([
    { version: 'v1.0', acc: 0.91 },
    { version: 'v1.1', acc: 0.93 },
    { version: 'v2.0', acc: 0.95 }
  ]);
});

module.exports = router;
