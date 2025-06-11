// /routes/apiRoutes.js

const express = require('express');
const router = express.Router();
const pool = require('../config/db'); // DB 설정 불러오기
// [수정] 새로 만든 서비스 함수를 import 목록에 추가합니다.
const { runFireSpreadPrediction, getGridData, getGridWithFuelInfo } = require('../services/simulationService');

// 산불 확산 예측 API
router.post('/predict-fire-spread', async (req, res) => {
    console.log(`[${new Date().toLocaleTimeString()}] /api/predict-fire-spread: 요청 수신 (ignition_id: ${req.body.ignition_id})`);
    const { ignition_id } = req.body;
    if (ignition_id == null) {
        return res.status(400).json({ error: '발화점 ID가 누락되었습니다.' });
    }
    try {
        const result = await runFireSpreadPrediction(pool, ignition_id); // Changed 'features' to 'result'
        res.json(result); // Send the entire result object
    } catch (err) {
        console.error('[API /predict-fire-spread] 오류:', err);
        res.status(500).json({ error: '서버 내부 오류가 발생했습니다.' });
    }
});

// 초기 격자 데이터 제공 API
router.get('/mapped-grid-data', async (req, res) => {
    try {
        const features = await getGridData(pool);
        res.json({ type: 'FeatureCollection', features });
    } catch (err) {
        console.error('[API /mapped-grid-data] 오류:', err);
        res.status(500).json({ error: 'DB 오류' });
    }
});


// [추가] 연료 등급 정보가 포함된 격자 데이터 제공 API
router.get('/grid-with-fuel-info', async (req, res) => {
    try {
        // 1. 서비스 함수를 호출하여 DB에서 데이터를 가져옵니다.
        const rows = await getGridWithFuelInfo(pool);

        // 2. 프론트엔드가 사용하기 좋은 GeoJSON 형태로 가공합니다.
        const features = rows.map(row => ({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [parseFloat(row.lng), parseFloat(row.lat)]
            },
            properties: {
                id: row.id,
                fuel_score: row.fuel_score 
            }
        }));

        // 3. GeoJSON FeatureCollection 형태로 최종 응답을 보냅니다.
        res.json({
            type: 'FeatureCollection',
            features: features
        });
    } catch (err) {
        console.error('[API /grid-with-fuel-info] 오류:', err);
        res.status(500).json({ error: 'DB 오류' });
    }
});

module.exports = router;
