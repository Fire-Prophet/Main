const request = require('supertest');
const app = require('../server'); // server.js에서 app 내보내야 사용 가능

test('POST /predict 예측 테스트', async () => {
  const res = await request(app).post('/predict').send({
    temp: 31, humidity: 25, wind: 6
  });
  expect(res.body).toHaveProperty('risk');
});
