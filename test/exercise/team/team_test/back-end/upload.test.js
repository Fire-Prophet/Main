const request = require('supertest');
const app = require('../server');
const path = require('path');

test('CSV 업로드 테스트', async () => {
  const res = await request(app)
    .post('/upload')
    .attach('file', path.join(__dirname, 'sample.csv'));
  expect(res.body.message).toBe('업로드 완료');
});
