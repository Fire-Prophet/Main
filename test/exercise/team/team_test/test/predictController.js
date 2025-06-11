const { loadLatestModel } = require('../../services/modelStore');

exports.predict = async (req, res) => {
  const { temp, humidity, wind } = req.body;
  const model = loadLatestModel();
  const pred = model.predict([[temp, humidity, wind]])[0];
  res.json({ risk: pred });
};
