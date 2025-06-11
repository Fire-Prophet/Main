const shap = require('shap');
const { loadLatestModel } = require('../../services/modelStore');

exports.explain = (req, res) => {
  const { temp, humidity, wind } = req.body;
  const model = loadLatestModel();
  const input = [[temp, humidity, wind]];
  const explainer = new shap.TreeExplainer(model);
  const shapValues = explainer.shap_values(input);
  res.json({ prediction: model.predict(input)[0], explanation: shapValues });
};
