// apiServer.js

const express = require('express');
const cors =require('cors');
const mysql = require('mysql2/promise'); // MySQL 연결을 위해 이미 사용 중
const turf = require('@turf/turf');
require('dotenv').config(); // .env 파일 로드

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

// --- 기존 MySQL 연결 풀 설정 (내 DB) ---
const pool = mysql.createPool({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || 'jonggu2020', // 본인 MySQL 암호
    database: process.env.DB_DATABASE || 'fire',
    waitForConnections: true,
    connectionLimit: parseInt(process.env.DB_CONNECTION_LIMIT) || 10,
    queueLimit: 0
});

// --- 동료의 외부 MySQL DB 연결 풀 설정 ---
const colleagueDbPool = mysql.createPool({
    host: process.env.COLLEAGUE_DB_HOST || 'probius.homes',          // 동료 DB 호스트 주소(IP)
    user: process.env.COLLEAGUE_DB_USER || 'root',                   // 동료 DB 사용자 이름
    port: parseInt(process.env.COLLEAGUE_DB_PORT) || 3306,                     // 동료 DB 포트 번호
    password: process.env.COLLEAGUE_DB_PASSWORD || 'probius', // ⭐⭐⭐ [필수] 동료 DB 비밀번호를 입력하세요!
    database: process.env.COLLEAGUE_DB_DATABASE || 'project_fire',       // 동료 DB의 데이터베이스 이름 (스키마)
    waitForConnections: true,
    connectionLimit: parseInt(process.env.COLLEAGUE_DB_CONNECTION_LIMIT) || 5, // 동료 DB이므로 커넥션 수를 적절히 조절
    queueLimit: 0
});


// --- 사용할 테이블명 상수 정의 ---
const FUEL_DATA_ASAN_CHEONAN_TABLE = 'fuel_data_asan_cheonan';
const PREDICT_POINTS_TABLE = 'fire_predict_points';
const KOREA_GRID_TABLE = 'korea_grid'; // 내 DB의 격자 테이블

// 루트 경로 핸들러
app.get('/', (req, res) => {
    res.status(200).send('산불 예측 API 서버가 정상적으로 실행 중입니다. (FireFighter Project)');
});

// === 아산/천안 상세 연료 데이터 제공 API ===
app.get('/api/fueldata/asancheonan', async (req, res) => {
    let connection;
    try {
        connection = await pool.getConnection(); // 내 DB 풀
        console.log(`[API /api/fueldata/asancheonan] MySQL 테이블 '${FUEL_DATA_ASAN_CHEONAN_TABLE}' 조회 시도...`);
        
        const [rows] = await connection.query(
            `SELECT id, coord_x, coord_y, total_fuel_strength, original_soil_id, soil_type_code, forest_type_code, soil_fuel_rating, forest_fuel_rating 
             FROM ${FUEL_DATA_ASAN_CHEONAN_TABLE}`
        );

        console.log(`[API /api/fueldata/asancheonan] ${rows.length}개 레코드 조회 완료. GeoJSON으로 변환 중...`);
        const features = rows.map(row => ({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [parseFloat(row.coord_x), parseFloat(row.coord_y)]
            },
            properties: {
                id: row.id,
                total_fuel_strength: row.total_fuel_strength,
            }
        }));
        res.json({ type: 'FeatureCollection', features });
        console.log(`[API /api/fueldata/asancheonan] GeoJSON 응답 전송 완료.`);
    } catch (err) {
        console.error('[API /api/fueldata/asancheonan] 오류:', err);
        res.status(500).json({ error: 'DB Error or Data Processing Error' });
    } finally {
        if (connection) connection.release();
    }
});

// === 산불 예측 시뮬레이션 관련 API ===

// 초기 예측 지점 데이터 제공
app.get('/api/fire-predict-points', async (req, res) => {
    let connection;
    try {
        connection = await pool.getConnection(); // 내 DB 풀
        console.log(`[API /api/fire-predict-points] MySQL 테이블 '${PREDICT_POINTS_TABLE}' 조회 시도...`);
        const [rows] = await connection.query(
            `SELECT id, coord_x, coord_y, total_fuel_strength FROM ${PREDICT_POINTS_TABLE}`
        );
        console.log(`[API /api/fire-predict-points] ${rows.length}개 레코드 조회 완료. GeoJSON으로 변환 중...`);
        const features = rows.map(row => ({
            type: 'Feature',
            geometry: { 
                type: 'Point', 
                coordinates: [parseFloat(row.coord_x), parseFloat(row.coord_y)] 
            },
            properties: {
                id: row.id,
                total_fuel_strength: row.total_fuel_strength,
                predicted_danger_level: 0
            }
        }));
        res.json({ type: 'FeatureCollection', features });
        console.log(`[API /api/fire-predict-points] GeoJSON 응답 전송 완료.`);
    } catch (err) {
        console.error('[API /api/fire-predict-points] 오류:', err);
        res.status(500).json({ error: 'DB Error' });
    } finally {
        if (connection) connection.release();
    }
});

// 산불 확산 예측 실행
app.post('/api/predict-fire-spread', async (req, res) => {
    const { ignition_id, humidity, windSpeed, windDirection } = req.body;
    if (ignition_id == null || humidity == null || windSpeed == null || windDirection == null) {
        return res.status(400).json({ error: '필수 입력값 누락' });
    }

    let connection;
    try {
        connection = await pool.getConnection(); // 내 DB 풀
        console.log(`[API /api/predict-fire-spread] MySQL 테이블 '${PREDICT_POINTS_TABLE}' 조회 시도...`);
        const [rows] = await connection.query(
            `SELECT id, coord_x, coord_y, total_fuel_strength FROM ${PREDICT_POINTS_TABLE}`
        );
        console.log(`[API /api/predict-fire-spread] ${rows.length}개 레코드 조회 완료. 확산 예측 계산 시작...`);
        
        const ignition = rows.find(r => r.id === ignition_id);
        if (!ignition) {
            console.warn(`[API /api/predict-fire-spread] 발화점 ID '${ignition_id}'를 '${PREDICT_POINTS_TABLE}' 테이블에서 찾을 수 없음.`);
            return res.status(404).json({ error: '발화점 데이터 없음' });
        }

        const ignitionPoint = turf.point([parseFloat(ignition.coord_x), parseFloat(ignition.coord_y)]);
        const features = rows.map(row => {
            const pt = turf.point([parseFloat(row.coord_x), parseFloat(row.coord_y)]);
            const distance = turf.distance(ignitionPoint, pt, { units: 'kilometers' });
            let score = row.total_fuel_strength ? Number(row.total_fuel_strength) : 1;

            if (distance < 0.1) score += 3;
            else if (distance < 0.3) score += 2;
            else if (distance < 0.7) score += 1;

            if (humidity < 35) score += 2;
            else if (humidity < 50) score += 1;
            else if (humidity > 75) score -= 1;

            let bearingTo = turf.bearing(ignitionPoint, pt);
            if (bearingTo < 0) bearingTo += 360;
            const windDir = Number(windDirection);
            const angleDiff = Math.abs(windDir - bearingTo);
            const normalizedAngleDiff = Math.min(angleDiff, 360 - angleDiff);

            if (normalizedAngleDiff < 30) score += Math.ceil(windSpeed / 1.5); 
            else if (normalizedAngleDiff < 60) score += Math.ceil(windSpeed / 3);   
            else if (normalizedAngleDiff > 150) score -= 1;
            score = Math.max(0, score);

            let danger = 0;
            if (row.id === ignition_id) danger = 4; 
            else if (score >= 8) danger = 3; 
            else if (score >= 6) danger = 2; 
            else if (score >= 4) danger = 1; 

            return {
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [parseFloat(row.coord_x), parseFloat(row.coord_y)] },
                properties: {
                    id: row.id,
                    total_fuel_strength: row.total_fuel_strength,
                    predicted_danger_level: danger,
                    is_ignition_point: row.id === ignition_id
                }
            };
        });
        res.json({ type: 'FeatureCollection', features });
        console.log(`[API /api/predict-fire-spread] 확산 예측 결과 전송 완료.`);
    } catch (err) {
        console.error('[API /api/predict-fire-spread] 오류:', err);
        res.status(500).json({ error: '서버 오류' });
    } finally {
        if (connection) connection.release();
    }
});


// === 기존 매핑된 격자 데이터 제공 API (내 DB) ===
// 이 엔드포인트는 이제 사용하지 않거나, 필요에 따라 유지할 수 있습니다.
// 만약 프론트엔드에서 더 이상 이 주소를 사용하지 않는다면 주석 처리하거나 삭제해도 됩니다.
app.get('/api/mapped-grid-data', async (req, res) => {
    let connection;
    try {
        connection = await pool.getConnection(); // 내 DB 풀
        console.log(`[API /api/mapped-grid-data] 내 DB '${KOREA_GRID_TABLE}' 조회 시도...`);
        const query = `
            SELECT id, lat, lng, imsangdo_FRTP_CD, soil_SLTP_CD 
            FROM ${KOREA_GRID_TABLE}
            WHERE imsangdo_FRTP_CD IS NOT NULL OR soil_SLTP_CD IS NOT NULL 
        `; // 이 쿼리는 KOREA_GRID_TABLE의 구조에 맞춰져 있습니다.
        const [rows] = await connection.query(query);
        const features = rows.map(row => ({
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [parseFloat(row.lng), parseFloat(row.lat)] },
            properties: { id: row.id, imsangdo_code: row.imsangdo_FRTP_CD, soil_code: row.soil_SLTP_CD }
        }));
        res.json({ type: 'FeatureCollection', features });
        console.log(`[API /api/mapped-grid-data] GeoJSON 응답 전송 완료.`);
    } catch (err) {
        console.error('[API /api/mapped-grid-data] 오류:', err);
        res.status(500).json({ error: 'DB Error' });
    } finally {
        if (connection) connection.release();
    }
});


// --- 동료 MySQL DB의 격자 데이터를 제공하는 새로운 API 엔드포인트 ---
app.get('/api/colleague-grid-data', async (req, res) => {
    let connection; 
    try {
        console.log(`[API /api/colleague-grid-data] 동료의 외부 MySQL DB 조회 시도...`);
        connection = await colleagueDbPool.getConnection(); // 동료 DB 풀에서 커넥션 가져오기

        const tableName = 'imported_fire_data_auto'; // 동료 DB의 테이블 이름

        // ⭐⭐⭐ [가정] 동료의 'imported_fire_data_auto' 테이블도 'id', 'lat', 'lng' 컬럼을 사용한다고 가정합니다.
        // 만약 컬럼명이 다르다면 아래 변수들을 실제 컬럼명으로 수정해야 합니다.
        const idCol = 'id';    // 예: 'gid', 'objectid', 또는 실제 ID 컬럼명
        const latCol = 'lat';  // 예: 'latitude', 'y_coord', 또는 실제 위도 컬럼명
        const lonCol = 'lng';  // 예: 'longitude', 'x_coord', 또는 실제 경도 컬럼명
        
        // 가져올 다른 속성 컬럼이 있다면 아래 주석을 풀고 실제 컬럼명으로 수정합니다.
        // const imsangdoCodeCol = 'imsangdo_FRTP_CD'; // 예시
        // const soilCodeCol = 'soil_SLTP_CD';       // 예시

        // 필요한 컬럼만 선택하도록 쿼리 수정
        // const query = `SELECT \`${idCol}\`, \`${latCol}\`, \`${lonCol}\`, \`${imsangdoCodeCol}\`, \`${soilCodeCol}\` FROM \`${tableName}\``;
        // 기본적으로 id, lat, lng만 가져오도록 설정. 필요시 위 주석처럼 다른 컬럼도 추가하세요.
        const query = `SELECT \`${idCol}\`, \`${latCol}\`, \`${lonCol}\` FROM \`${tableName}\``;


        const [rows] = await connection.query(query); // MySQL 쿼리 실행
        console.log(`[API /api/colleague-grid-data] '${tableName}' 테이블에서 ${rows.length}개 레코드 조회 완료. GeoJSON으로 변환 중...`);

        const features = rows.map(row => ({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [parseFloat(row[lonCol]), parseFloat(row[latCol])] // 경도, 위도 순서
            },
            properties: {
                id: row[idCol],
                // 만약 다른 속성도 가져왔다면 여기에 추가합니다.
                // imsangdo_code: row[imsangdoCodeCol],
                // soil_code: row[soilCodeCol],
            }
        }));

        res.json({ type: 'FeatureCollection', features });
        console.log(`[API /api/colleague-grid-data] GeoJSON 응답 전송 완료.`);

    } catch (err) {
        console.error('[API /api/colleague-grid-data] 오류:', err);
        res.status(500).json({ error: 'External DB Error or Data Processing Error' });
    } finally {
        if (connection) {
            connection.release(); 
        }
    }
});


// 서버 시작
app.listen(port, () => {
    console.log(`🔥 산불 예측 API 서버 running at http://localhost:${port}`);
    console.log(`   아산/천안 연료 데이터 API (GET): http://localhost:${port}/api/fueldata/asancheonan`);
    console.log(`   초기 예측 지점 API (GET): http://localhost:${port}/api/fire-predict-points`);
    console.log(`   산불 확산 예측 API (POST): http://localhost:${port}/api/predict-fire-spread`);
    console.log(`   (내 DB) 매핑된 격자 데이터 API (GET): http://localhost:${port}/api/mapped-grid-data`);
    console.log(`   (동료 DB) 격자 데이터 API (GET): http://localhost:${port}/api/colleague-grid-data`);
});
