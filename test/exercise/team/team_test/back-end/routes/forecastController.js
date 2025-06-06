exports.predictTomorrow = (req, res) => {
  const { temp } = req.body;
  const tomorrow = temp + 1; // 가정: 기온 상승
  const risk = tomorrow > 30 ? '위험' : '보통';
  res.json({ tomorrowTemp: tomorrow, risk });
};
