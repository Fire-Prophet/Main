const mongoose = require('mongoose');

const FeedbackSchema = new mongoose.Schema({
  user: String,
  message: String,
  createdAt: Date
});

module.exports = mongoose.model('Feedback', FeedbackSchema);
