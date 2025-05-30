// .env 파일 로드 (가장 먼저!)
require('dotenv').config();

// 필요한 모듈 가져오기
const express = require('express');
const mysql = require('mysql2/promise'); // mysql2의 Promise 버전 사용
const cors = require('cors');
const admin = require('firebase-admin'); // Firebase Admin SDK

// Express 앱 초기화
const app = express();
const port = process.env.API_PORT || 3001;

// --- Firebase Admin 초기화 ---
try {
    const serviceAccount = require(process.env.FIREBASE_CRED_PATH);
    admin.initializeApp({
        credential: admin.credential.cert(serviceAccount),
        databaseURL: process.env.FIREBASE_DB_URL
    });
    console.log("Firebase Admin SDK가 성공적으로 초기화되었습니다.");
} catch (error) {
    console.error("Firebase Admin SDK 초기화 오류:", error);
    console.error("FIREBASE_CRED_PATH와 FIREBASE_DB_URL이 .env 파일에 올바르게 설정되었는지 확인하세요.");
    process.exit(1); // 초기화 실패 시 서버 종료
}
// -----------------------------

// --- 미들웨어 설정 ---
// CORS 설정: React 앱 (예: localhost:5173)에서 오는 요청 허용
app.use(cors({
    origin: 'http://localhost:5173' // React 앱의 주소
}));
// Body Parser 추가: POST, PUT 요청의 body (JSON)를 파싱
app.use(express.json());
// -------------------

// --- MySQL 연결 풀 설정 ---
const pool = mysql.createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_DATABASE,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
})

console.log("MySQL 연결 풀이 설정되었습니다.");
// -------------------------

// --- API 엔드포인트 ---

// GET /api/parkinglots: 모든 주차장 정보 조회
app.get('/api/parkinglots', async (req, res) => {
    try {
        const [rows] = await pool.query("SELECT LotID, Name, Address, Latitude, Longitude, TotalSpaces, HourlyRate FROM ParkingLots");
        res.json(rows);
    } catch (error) {
        console.error("GET /api/parkinglots 오류:", error);
        res.status(500).json({ error: "데이터베이스 조회 중 오류가 발생했습니다." });
    }
});

// GET /api/parkinglots/:id: 특정 주차장 정보 조회
app.get('/api/parkinglots/:id', async (req, res) => {
    const { id } = req.params;
    try {
        const [rows] = await pool.query("CALL Find_Parking_Lot_By_ID(?)", [id]);
        if (rows[0] && rows[0].length > 0) {
            res.json(rows[0][0]);
        } else {
            res.status(404).json({ error: "주차장을 찾을 수 없습니다." });
        }
    } catch (error) {
        console.error(`GET /api/parkinglots/${id} 오류:`, error);
        res.status(500).json({ error: "데이터베이스 조회 중 오류가 발생했습니다." });
    }
});

// POST /api/parkinglots: 새 주차장 추가
app.post('/api/parkinglots', async (req, res) => {
    const { Name, Address, Latitude, Longitude, TotalSpaces, HourlyRate } = req.body;
    if (!Name || !Address || !Latitude || !Longitude || !TotalSpaces) {
        return res.status(400).json({ error: "필수 입력값이 누락되었습니다." });
    }
    try {
        const [rows] = await pool.query(
            "CALL Add_Parking_Lot(?, ?, ?, ?, ?, ?)",
            [Name, Address, Latitude, Longitude, TotalSpaces, HourlyRate || 0]
        );
        const newLotId = rows[0][0].NewLotID;
        console.log(`새 주차장 추가 완료 (ID: ${newLotId})`);
        res.status(201).json({ message: "주차장이 성공적으로 추가되었습니다.", newLotId: newLotId });
    } catch (error) {
        console.error("POST /api/parkinglots 오류:", error);
        res.status(500).json({ error: "데이터베이스 추가 중 오류가 발생했습니다." });
    }
});

// PUT /api/parkinglots/:id: 특정 주차장 정보 수정
app.put('/api/parkinglots/:id', async (req, res) => {
    const { id } = req.params;
    const { Name, Address, Latitude, Longitude, TotalSpaces, HourlyRate } = req.body;
    if (!Name || !Address || !Latitude || !Longitude || !TotalSpaces) {
        return res.status(400).json({ error: "필수 입력값이 누락되었습니다." });
    }
    try {
        const [rows] = await pool.query(
            "CALL Update_Parking_Lot_By_ID(?, ?, ?, ?, ?, ?, ?)",
            [id, Name, Address, Latitude, Longitude, TotalSpaces, HourlyRate || 0]
        );
        if (rows[0][0].UpdatedRows > 0) {
            console.log(`주차장 수정 완료 (ID: ${id})`);
            res.status(200).json({ message: "주차장 정보가 성공적으로 수정되었습니다." });
        } else {
             res.status(404).json({ error: "수정할 주차장을 찾을 수 없거나 변경된 내용이 없습니다." });
        }
    } catch (error) {
        console.error(`PUT /api/parkinglots/${id} 오류:`, error);
        res.status(500).json({ error: "데이터베이스 수정 중 오류가 발생했습니다." });
    }
});

// DELETE /api/parkinglots/:id: 주차장 삭제
app.delete('/api/parkinglots/:id', async (req, res) => {
    const { id } = req.params;
    const lotIdStr = `LotID_${id}`;
    let connection;
    try {
        connection = await pool.getConnection();
        await connection.beginTransaction(); // 트랜잭션 시작

        const [mysqlResult] = await connection.query("CALL Delete_Parking_Lot_By_ID(?)", [id]);

        if (mysqlResult[0][0].DeletedRows === 0) {
            await connection.rollback();
            return res.status(404).json({ error: "삭제할 주차장을 찾을 수 없습니다." });
        }

        const firebaseRef = admin.database().ref(`/ParkingStatus/${lotIdStr}`);
        await firebaseRef.remove();

        await connection.commit(); // 커밋

        console.log(`주차장 삭제 완료 (ID: ${id})`);
        res.status(200).json({ message: "주차장이 성공적으로 삭제되었습니다." });

    } catch (error) {
        if (connection) await connection.rollback();
        console.error(`DELETE /api/parkinglots/${id} 오류:`, error);
        res.status(500).json({ error: "데이터 삭제 중 오류가 발생했습니다." });
    } finally {
        if (connection) connection.release();
    }
});

// -------------------------

// --- 서버 시작 ---
app.listen(port, () => {
    console.log(`API 서버가 http://localhost:${port} 에서 실행 중입니다.`);
});
// ---------------
