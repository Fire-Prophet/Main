const Feedback = require('../models/Feedback');

exports.submitFeedback = async (req, res) => {
  const { message, user } = req.body;
  const feedback = new Feedback({ message, user, createdAt: new Date() });
  await feedback.save();
  res.json({ success: true, msg: '의견 감사합니다!' });
};
