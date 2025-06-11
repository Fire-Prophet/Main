// src/components/VWorldMap/mapConfig.js

import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';
import Circle from 'ol/style/Circle';

export const VWORLD_XYZ_URL = 'http://xdworld.vworld.kr:8080/2d/Base/201802/{z}/{x}/{y}.png?apiKey=B60B525E-129D-3B8B-880F-77C24CF86AE3';

// --- 산불 확산 예측 범례 색상 및 설명 ---
export const fireSpreadColors = {
    burning: 'rgba(255, 0, 0, 0.8)',      // 붉은색 (연소 중)
    predicted: 'rgba(255, 255, 0, 0.8)',   // 노란색 (예상 경로)
    burned_out: 'rgba(0, 0, 0, 0.8)',     // 검은색 (연소 완료)
    safe: 'rgba(0, 128, 0, 0.7)'         // 초록색 (안전)
};
export const fireSpreadDescriptions = {
    burning: '연소 중',
    predicted: '확산 예상 경로',
    burned_out: '연소 완료',
    safe: '안전'
};

// --- 산악기상관측소 마커 스타일 및 범례 ---
export const mountainMarkerStyle = new Style({
    image: new Circle({
        radius: 7,
        fill: new Fill({ color: 'rgba(0, 128, 0, 0.8)' }),
        stroke: new Stroke({ color: 'white', width: 1.5 })
    })
});
export const mountainMarkerLegendInfo = {
    description: '산악기상관측소',
    styleProps: { image: { type: 'circle', radius: 7, fill: { color: 'rgba(0, 128, 0, 0.8)' }, stroke: { color: 'white', width: 1.5 } } }
};


// --- 논리적인 레이어 그룹 설정 ---
export const logicalLayersConfig = [
    // --- Vector 레이어들 ---
    {
        name: '산악기상관측소 마커',
        type: 'mountain_station_markers',
        visible: true,
        isCollapsibleLegend: false,
        legendInfo: mountainMarkerLegendInfo,
    },
    { 
        name: '전국 격자 데이터',
        type: 'mapped_grid_data_vector', 
        url: 'http://localhost:3001/api/mapped-grid-data', 
        visible: true, 
        isCollapsibleLegend: true,
        defaultCollapsed: false,
        legendInfo: {
            title: '격자 상태',
            type: 'simple_point_legend',
            description: '안전 (클릭하여 발화점으로 지정)',
            style: { 
                color: 'rgba(0, 128, 0, 0.6)',
                radius: 3
            }
        },
    },
    {
        name: '산불 확산 시뮬레이션',
        type: 'fire_prediction_vector',
        visible: true,
        isCollapsibleLegend: true,
        defaultCollapsed: false,
        legendInfo: {
            title: '산불 확산 예측 결과',
            type: 'colormap_fire_spread',
            colors: fireSpreadColors,
            descriptions: fireSpreadDescriptions
        },
    },
];