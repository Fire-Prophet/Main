const express = require('express');
const path = require('path');
const app = express();
const port = 3000;

// EJS 템플릿 엔진 설정
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// POST 요청의 body를 파싱하기 위한 미들웨어
app.use(express.urlencoded({ extended: true }));
// 정적 파일(CSS, JS 등)을 위한 미들웨어 (선택 사항)
// app.use(express.static('public'));

// 게시물을 저장할 메모리 내 배열
let posts = [
    { id: 1, title: "기사의 첫 번째 기록", content: "세상은 나를 잊었지만, 나는 아직 이곳에 있다." },
    { id: 2, title: "방랑의 시작", content: "나의 이야기를 찾아서, 이제 길을 떠난다." }
];
let nextId = 3; // 다음 게시물 ID

// 메인 페이지: 게시물 목록 표시
app.get('/', (req, res) => {
    res.render('index', { posts: posts });
});

// 새 글 작성 페이지
app.get('/new', (req, res) => {
    res.render('new');
});

// 새 글 생성 처리
app.post('/create', (req, res) => {
    const { title, content } = req.body;
    if (title && content) {
        posts.push({ id: nextId++, title, content });
        res.redirect('/');
    } else {
        res.status(400).send("제목과 내용을 모두 입력해야 합니다.");
    }
});

// 서버 시작
app.listen(port, () => {
    console.log(`블로그 서버가 http://localhost:${port} 에서 실행 중입니다.`);
});
