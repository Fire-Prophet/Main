const { loadLatestModel } = require('../../services/modelStore');
const test = require('../../../data/test.json');

exports.evaluateModel = (req, res) => {
  const model = loadLatestModel();
  const X = test.map(row => [row.temp, row.humidity, row.wind]);
  const y = test.map(row => row.label);
  const preds = model.predict(X);
  const correct = preds.filter((p, i) => p === y[i]).length;
  res.json({ accuracy: correct / y.length });
};
