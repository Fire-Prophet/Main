
// backend/apiServer.js (최종 해결책 v2)

require('dotenv').config();

const express = require('express');
const cors = require('cors');
const path = require('path');
const apiRoutes = require('./routes/apiRoutes');

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

// 1. API 라우트를 먼저 등록합니다.
// '/api'로 시작하는 요청은 여기서 처리됩니다.
app.use('/api', apiRoutes);

// 2. React 빌드 폴더를 static으로 지정합니다.
// css, js, image 파일 등 실제 파일 요청은 여기서 처리됩니다.
const buildPath = path.join(__dirname, '..', 'firefighter', 'build');
app.use(express.static(buildPath));

// 3. [수정] 위에서 처리되지 않은 모든 요청을 index.html로 보내는 최후의 미들웨어
// 이것이 문제가 되었던 app.get('/*', ...)를 대체합니다.
// 이 미들웨어는 라우팅 스택의 맨 마지막에 위치해야 합니다.
app.use((req, res, next) => {
    res.sendFile(path.join(buildPath, 'index.html'));
});

// 서버 실행
app.listen(port, '0.0.0.0', () => {
    console.log(`✅ 서버가 http://0.0.0.0:${port} 에서 성공적으로 실행되었습니다.`);
  });
  