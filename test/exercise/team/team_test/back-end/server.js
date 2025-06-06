const express = require('express');
const cors = require('cors');
const app = express();
const predictRouter = require('./routes/predict');
const uploadRouter = require('./routes/upload');
const geoRouter = require('./routes/geo');
const statusRouter = require('./routes/status');
const logger = require('./middleware/logger');

app.use(cors());
app.use(express.json());
app.use(logger);

app.use('/predict', predictRouter);
app.use('/upload', uploadRouter);
app.use('/geo', geoRouter);
app.use('/status', statusRouter);

app.listen(5000, () => {
  console.log('🔥 Server running on port 5000');
});
