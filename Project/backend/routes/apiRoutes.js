// /routes/apiRoutes.js

const express = require('express');
const router = express.Router();
const pool = require('../config/db'); // DB 설정 불러오기
const { runFireSpreadPrediction, getGridData } = require('../services/simulationService'); // 서비스 로직 불러오기

// 산불 확산 예측 API
router.post('/predict-fire-spread', async (req, res) => {
    console.log(`[${new Date().toLocaleTimeString()}] /api/predict-fire-spread: 요청 수신 (ignition_id: ${req.body.ignition_id})`);
    const { ignition_id } = req.body;
    if (ignition_id == null) {
        return res.status(400).json({ error: '발화점 ID가 누락되었습니다.' });
    }
    try {
        const features = await runFireSpreadPrediction(pool, ignition_id);
        res.json({ type: 'FeatureCollection', features });
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

module.exports = router;