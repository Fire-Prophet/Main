module.exports = (req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    if (duration > 500) {
      console.warn(`⚠️ 느린 요청: ${req.method} ${req.url} - ${duration}ms`);
    }
  });
  next();
};
