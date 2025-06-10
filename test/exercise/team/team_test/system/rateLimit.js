const rateLimit = require('express-rate-limit');

module.exports = rateLimit({
  windowMs: 60 * 1000, // 1분
  max: 30, // IP당 30회
  message: '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.'
});
