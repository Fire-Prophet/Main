const pickle = require('picklejs');
let cached = null;

exports.loadLatestModel = () => {
  if (!cached) {
    cached = pickle.loadSync('models/fire_model_latest.pkl');
  }
  return cached;
};
