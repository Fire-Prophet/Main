const express = require('express');
const bodyParser = require('body-parser'); // POST 요청 본문 파싱을 위함

const app = express();
const port = 3000;

// 미들웨어 설정
app.use(bodyParser.json()); // JSON 형식의 요청 본문을 파싱합니다.
app.use(bodyParser.urlencoded({ extended: true })); // URL-encoded 형식의 요청 본문을 파싱합니다.

// 간단한 인메모리 데이터베이스 (실제 앱에서는 데이터베이스를 사용합니다)
let posts = [
    { id: 1, title: '첫 번째 게시물', content: 'Node.js Express API 예시입니다.' },
    { id: 2, title: '두 번째 게시물', content: 'RESTful API 디자인 패턴을 따릅니다.' }
];
let nextId = 3; // 다음 게시물 ID

// 루트 경로 GET 요청 핸들러
app.get('/', (req, res) => {
    res.send('환영합니다! /api/posts 경로로 접속하여 게시물을 확인하세요.');
});

// 모든 게시물 가져오기 (GET /api/posts)
app.get('/api/posts', (req, res) => {
    console.log('GET /api/posts 요청 수신');
    res.status(200).json(posts);
});

// 특정 게시물 가져오기 (GET /api/posts/:id)
app.get('/api/posts/:id', (req, res) => {
    const id = parseInt(req.params.id); // URL 파라미터는 문자열이므로 숫자로 변환
    const post = posts.find(p => p.id === id);
    if (post) {
        console.log(`GET /api/posts/${id} 요청 수신: 게시물 발견`);
        res.status(200).json(post);
    } else {
        console.log(`GET /api/posts/${id} 요청 수신: 게시물을 찾을 수 없음`);
        res.status(404).json({ message: '게시물을 찾을 수 없습니다.' });
    }
});

// 새 게시물 생성 (POST /api/posts)
app.post('/api/posts', (req, res) => {
    const { title, content } = req.body; // 요청 본문에서 title과 content 추출
    if (!title || !content) {
        console.log('POST /api/posts 요청 수신: 유효하지 않은 입력');
        return res.status(400).json({ message: '제목과 내용을 모두 입력해야 합니다.' });
    }
    const newPost = { id: nextId++, title, content };
    posts.push(newPost);
    console.log(`POST /api/posts 요청 수신: 새 게시물 추가됨 (ID: ${newPost.id})`);
    res.status(201).json(newPost); // 201 Created 상태 코드 반환
});

// 특정 게시물 업데이트 (PUT /api/posts/:id)
app.put('/api/posts/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const { title, content } = req.body;
    let postFound = false;

    posts = posts.map(p => {
        if (p.id === id) {
            postFound = true;
            console.log(`PUT /api/posts/${id} 요청 수신: 게시물 업데이트`);
            return { ...p, title: title || p.title, content: content || p.content };
        }
        return p;
    });

    if (postFound) {
        res.status(200).json(posts.find(p => p.id === id));
    } else {
        console.log(`PUT /api/posts/${id} 요청 수신: 게시물을 찾을 수 없음`);
        res.status(404).json({ message: '게시물을 찾을 수 없습니다.' });
    }
});

// 특정 게시물 삭제 (DELETE /api/posts/:id)
app.delete('/api/posts/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const initialLength = posts.length;
    posts = posts.filter(p => p.id !== id);

    if (posts.length < initialLength) {
        console.log(`DELETE /api/posts/${id} 요청 수신: 게시물 삭제됨`);
        res.status(204).send(); // 204 No Content (성공적으로 삭제되었지만 응답 본문 없음)
    } else {
        console.log(`DELETE /api/posts/${id} 요청 수신: 게시물을 찾을 수 없음`);
        res.status(404).json({ message: '게시물을 찾을 수 없습니다.' });
    }
});

// 서버 시작
app.listen(port, () => {
    console.log(`서버가 http://localhost:${port} 에서 실행 중입니다.`);
    console.log(`API 엔드포인트: http://localhost:${port}/api/posts`);
});
