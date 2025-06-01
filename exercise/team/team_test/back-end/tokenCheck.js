module.exports = (req, res, next) => {
  const token = req.headers.authorization;
  if (token === 'Bearer admin-token') {
    next();
  } else {
    res.status(401).json({ error: '인증 실패' });
  }
};
