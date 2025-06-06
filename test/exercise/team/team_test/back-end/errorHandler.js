module.exports = (err, req, res, next) => {
  console.error('❗', err.stack);
  res.status(500).json({ error: '서버 내부 오류', detail: err.message });
};
