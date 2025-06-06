module.exports = (req, res, next) => {
  const role = req.headers['x-role'];
  if (role === 'admin') next();
  else res.status(403).json({ error: '관리자만 접근 가능합니다' });
};
