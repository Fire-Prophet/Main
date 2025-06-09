// apiServer.js

// .env 파일의 환경 변수를 로드합니다.
require('dotenv').config();

const express = require('express');
const cors = require('cors');
const apiRoutes = require('./routes/apiRoutes'); // 라우터 파일 불러오기

const app = express();
const port = 3001;

// 미들웨어 설정
app.use(cors());
app.use(express.json());

// '/api' 경로로 들어오는 모든 요청을 apiRoutes에서 처리하도록 설정
app.use('/api', apiRoutes);

// 서버 실행
app.listen(port, () => {
    console.log(`🔥 산불 예측 API 서버가 http://localhost:${port} 에서 실행 중입니다.`);
});