exports.checkDanger = (req, res) => {
  const { temp, humidity, wind } = req.body;
  if (temp > 35 && humidity < 20 && wind > 7) {
    res.json({ alert: '🔥 긴급 경보: 산불 발생 가능성 높음!' });
  } else {
    res.json({ alert: '⚠️ 현재는 안정적입니다.' });
  }
};
