const cron = require('node-cron');
const axios = require('axios');

cron.schedule('0 9 * * *', async () => {
  console.log('[예측 자동 실행] 매일 9시');
  await axios.post('http://localhost:5000/predict', {
    temp: 30, humidity: 20, wind: 5
  });
});
