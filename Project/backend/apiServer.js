// apiServer.js

const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise');
const turf = require('@turf/turf');
const db = require('./firebaseAdmin');
const { mountainStationsData } = require('./mountainStations');

class PriorityQueue {
    constructor() { this.elements = []; }
    enqueue(element, priority) { this.elements.push({ element, priority }); this.sort(); }
    dequeue() { return this.elements.shift().element; }
    sort() { this.elements.sort((a, b) => a.priority - b.priority); }
    isEmpty() { return this.elements.length === 0; }
}

const app = express();
const port = 3001;
app.use(cors());
app.use(express.json());

const pool = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: 'jonggu2020',
    database: 'fire',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

const KOREA_GRID_TABLE = 'korea_grid';

const getFuelScore = (imsangdoCode) => imsangdoCode ? ({'1':5,'3':4,'2':3,'4':2}[imsangdoCode] ?? 0) : 0;
const getSlopeFactor = (code1) => {
    if(!code1) return 1.0;
    return {'01':1.5,'02':1.5,'03':1.5,'08':1.5,'12':1.5,'04':0.8,'05':0.8,'06':0.8,'07':0.8,'11':0.8,'10':0.5}[code1] ?? 1.0;
}
const getMoistureFactor = (soilCode, humidity) => {
    let factor = 1.0;
    if (humidity < 35) factor = 1.5;
    else if (humidity < 50) factor = 1.2;
    else if (humidity > 75) factor = 0.7;
    if(!soilCode) return factor;
    if (['01','02','05','06','07','08','09','10','11','13','14','15','16','17','18','19','23','24'].includes(soilCode)) return factor * 1.2;
    if (['03','12','20'].includes(soilCode)) return factor * 0.8;
    if (['82','91','92','93','94','95','97','99','27','28','29'].includes(soilCode)) return 0;
    return factor;
}
const getWindFactor = (windSpeed, windDirection, bearing) => {
    const angleDiff = Math.abs((windDirection - bearing + 180) % 360 - 180);
    let factor = 1.0;
    if (angleDiff < 45) factor += (windSpeed / 4);
    else if (angleDiff < 90) factor += (windSpeed / 8);
    return Math.max(0.5, factor);
}

const findNeighbors = (currentPoint, allPoints) => {
    const searchRadius = 0.03;
    const [lon, lat] = currentPoint.coordinates;
    const candidates = allPoints
        .filter(p => p.id !== currentPoint.id && p.lat > lat - searchRadius && p.lat < lat + searchRadius && p.lng > lon - searchRadius && p.lng < lon + searchRadius)
        .map(p => ({ point: p, dist: turf.distance(currentPoint.coordinates, p.coordinates) }))
        .filter(item => item.dist > 0 && item.dist < 2.5)
        .sort((a, b) => a.dist - b.dist);
    return candidates.slice(0, 8).map(item => item.point.id);
}

app.post('/api/predict-fire-spread', async (req, res) => {
    const startTime = Date.now();
    console.log(`[${new Date().toLocaleTimeString()}] /api/predict-fire-spread: 요청 수신 (ignition_id: ${req.body.ignition_id})`);
    const { ignition_id } = req.body;
    if (ignition_id == null) return res.status(400).json({ error: '발화점 ID가 누락되었습니다.' });

    let connection;
    try {
        connection = await pool.getConnection();
        const [rows] = await connection.query(`SELECT id, lat, lng, imsangdo_frtp_cd, soil_tpgrp_tpcd, soil_sltp_cd FROM ${KOREA_GRID_TABLE}`);
        
        const allPoints = rows.map(row => ({...row, coordinates: [parseFloat(row.lng), parseFloat(row.lat)]}));
        const pointMap = new Map(allPoints.map(p => [p.id, p]));

        const ignitionPoint = pointMap.get(ignition_id);
        if (!ignitionPoint) return res.status(404).json({ error: '발화점 데이터를 찾을 수 없습니다.' });
        
        const nearestStation = mountainStationsData.reduce((p, c) => (turf.distance(ignitionPoint.coordinates, [c.longitude, c.latitude]) < turf.distance(ignitionPoint.coordinates, [p.longitude, p.latitude]) ? c : p));
        const weatherRef = db.ref(`weatherdata/${nearestStation.obsid}`);
        const snapshot = await weatherRef.once('value');
        const weatherData = snapshot.val() || {};
        const humidity = weatherData.hm2m ?? 50, windSpeed = weatherData.ws2m ?? 3, windDirection = weatherData.wd2m ?? 0;
        
        console.log(` -> 날씨 정보 로드 완료 (관측소: ${nearestStation.name})`);
        
        const simResults = new Map();
        allPoints.forEach(p => simResults.set(p.id, { ignitionTime: null, burnoutTime: null }));

        const eventQueue = new PriorityQueue();
        const initialIgnitionResult = simResults.get(ignition_id);
        initialIgnitionResult.ignitionTime = 0;
        initialIgnitionResult.burnoutTime = getFuelScore(ignitionPoint.imsangdo_frtp_cd) * 1200;
        eventQueue.enqueue(ignition_id, 0);
        
        let processedCount = 0;
        console.log(` -> 시뮬레이션 루프 시작...`);

        while (!eventQueue.isEmpty()) {
            const currentPointId = eventQueue.dequeue();
            const currentPoint = pointMap.get(currentPointId);
            const currentResult = simResults.get(currentPointId);

            processedCount++;
            if (processedCount % 100 === 0) {
                console.log(`   ... 처리된 포인트: ${processedCount}개, 큐 크기: ${eventQueue.elements.length}`);
            }

            if (currentResult.ignitionTime > 6 * 3600) continue;

            const neighborIds = findNeighbors(currentPoint, allPoints);

            for (const neighborId of neighborIds) {
                const neighbor = pointMap.get(neighborId);
                const neighborResult = simResults.get(neighborId);
                if (neighborResult.ignitionTime != null) continue;

                const fuelScore = getFuelScore(neighbor.imsangdo_frtp_cd);
                if (fuelScore === 0) continue;

                const distance = turf.distance(currentPoint.coordinates, neighbor.coordinates);
                const bearing = turf.bearing(currentPoint.coordinates, neighbor.coordinates);
                const slopeFactor = getSlopeFactor(neighbor.soil_tpgrp_tpcd);
                const moistureFactor = getMoistureFactor(neighbor.soil_sltp_cd, humidity);
                const windFactor = getWindFactor(windSpeed, windDirection, bearing);

                const rosScore = fuelScore * slopeFactor * moistureFactor * windFactor;
                if (rosScore < 2) continue;

                const timeToTravel = (distance * 3600) / rosScore;
                const newIgnitionTime = currentResult.ignitionTime + timeToTravel;

                if (newIgnitionTime < (neighborResult.ignitionTime ?? Infinity)) {
                    neighborResult.ignitionTime = newIgnitionTime;
                    neighborResult.burnoutTime = newIgnitionTime + (fuelScore * 1200);
                    eventQueue.enqueue(neighborId, newIgnitionTime);
                }
            }
        }

        const endTime = Date.now();
        console.log(` -> 시뮬레이션 루프 종료. 총 소요 시간: ${(endTime - startTime)/1000}초, 총 처리된 포인트: ${processedCount}개`);

        const features = allPoints.map(p => {
            const result = simResults.get(p.id);
            return {
                type: 'Feature', geometry: { type: 'Point', coordinates: p.coordinates },
                // ⭐ 수정: status 속성 제거
                properties: { id: p.id, ignitionTime: result.ignitionTime, burnoutTime: result.burnoutTime }
            };
        });

        res.json({ type: 'FeatureCollection', features });

    } catch (err) {
        console.error('[API /predict-fire-spread] 오류:', err);
        res.status(500).json({ error: '서버 내부 오류가 발생했습니다.' });
    } finally {
        if (connection) connection.release();
    }
});

app.get('/api/mapped-grid-data', async (req, res) => {
    let connection;
    try {
        connection = await pool.getConnection();
        const [rows] = await connection.query(`SELECT id, lat, lng FROM ${KOREA_GRID_TABLE}`);
        const features = rows.map(row => ({
            type: 'Feature', geometry: { type: 'Point', coordinates: [parseFloat(row.lng), parseFloat(row.lat)] },
            properties: { id: row.id }
        }));
        res.json({ type: 'FeatureCollection', features });
    } catch (err) {
        res.status(500).json({ error: 'DB 오류' });
    } finally {
        if (connection) connection.release();
    }
});

app.listen(port, () => {
    console.log(`🔥 산불 예측 API 서버가 http://localhost:${port} 에서 실행 중입니다.`);
});
