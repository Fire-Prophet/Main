// src/components/VWorldMap/mapConfig.js

import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';
import Circle from 'ol/style/Circle';

export const VWORLD_XYZ_URL = 'http://xdworld.vworld.kr:8080/2d/Base/201802/{z}/{x}/{y}.png?apiKey=B60B525E-129D-3B8B-880F-77C24CF86AE3';

// --- 아산/천안 토양도 범례 정보 ---
export const asanCheonanSoilColorMap = {
    '01': '#c8824c', '02': '#c8ab4f', '03': '#c6c9b7', '05': '#efc27e',
    '06': '#19ee12', '28': '#7182d9', '82': '#d2533f', '91': '#62e0d6',
    '93': '#8ce7b5', '94': '#de386f', '95': '#80ee19', '99': '#128cd2',
};
export const asanCheonanSoilCodeDescriptions = {
    '01': '갈색건조산림토양(1)', '02': '갈색약건산림토양(2)', '03': '갈색적윤산림토양(3)',
    '05': '적색계갈색건조산림토양(5)', '06': '적색계갈색약건산림토양(6)', '28': '암쇄토양(28)',
    '82': '제지(R)', '91': '주거지(S)', '93': '경작지(C)', '94': '수채(W)',
    '95': '과수원(O)', '99': '기타(E)',
};

// --- 임상도 범례 정보 ---
export const imsangdoColorMap = {
    '0': '#D2B48C', '1': '#38A800', '2': '#B370D7', '3': '#34CA96', '4': '#A1DDA1',
};
export const imsangdoCodeDescriptions = {
    '0': '무립목지 / 비산림', '1': '침엽수림 (수관 75% 이상)',
    '2': '활엽수림 (수관 75% 이상)', '3': '혼효림 (침엽 25~75%)', '4': '죽림',
};

// --- "아산천안 연료 강도" 표시용 색상 정의 ---
export const fuelStrengthColorMap = {
    1: 'rgba(240,240,240,0.7)', 2: 'rgba(220,220,220,0.7)', // 매우 낮음
    3: 'rgba(102,255,102,0.7)', 4: 'rgba(51,204,51,0.7)',  // 낮음 (연초록, 초록)
    5: 'rgba(255,255,102,0.7)', 6: 'rgba(255,204,51,0.7)', // 보통 (노랑, 주황색계열 노랑)
    7: 'rgba(255,153,51,0.7)', 8: 'rgba(255,102,0,0.7)',   // 높음 (주황, 빨강색계열 주황)
    9: 'rgba(255,51,0,0.7)', 10: 'rgba(204,0,0,0.7)',      // 매우 높음 (빨강, 진한빨강)
    'DEFAULT': 'rgba(180,180,180,0.5)' // 기본 또는 값 없음
};

// --- 등산로 스타일 및 범례 ---
export const hikingTrailStyle = new Style({
    stroke: new Stroke({ color: '#8B4513', width: 2.5, lineDash: [6, 6] }),
});
export const hikingTrailLegendInfo = {
    description: '등산로',
    styleProps: { stroke: { color: '#8B4513', width: 2.5, lineDash: [6, 6] } }
};

// --- 산악기상관측소 마커 스타일 및 범례 ---
export const mountainMarkerStyle = new Style({
    image: new Circle({
        radius: 7,
        fill: new Fill({ color: 'rgba(0, 128, 0, 0.8)' }), // 초록색 계열
        stroke: new Stroke({ color: 'white', width: 1.5 })
    })
});
export const mountainMarkerLegendInfo = {
    description: '산악기상관측소',
    styleProps: { image: { type: 'circle', radius: 7, fill: { color: 'rgba(0, 128, 0, 0.8)' }, stroke: { color: 'white', width: 1.5 } } }
};

// --- 논리적인 레이어 그룹 설정 ---
export const logicalLayersConfig = [
    // --- WMS 레이어들 ---
    {
        name: '아산천안 토양', type: 'soil',
        layerNames: ['ne:Asan_Cheonan_Soil_1', 'ne:Asan_Cheonan_Soil_2', 'ne:Asan_Cheonan_Soil_3'],
        url: 'http://localhost:8080/geoserver/ne/wms', // GeoServer 주소는 환경에 맞게 확인 필요
        visible: false, isCollapsibleLegend: true, defaultCollapsed: true,
        colorMap: asanCheonanSoilColorMap, codeDescriptions: asanCheonanSoilCodeDescriptions,
        filterAttribute: 'SLTP_CD',
    },
    {
        name: '아산천안 임상도', type: 'imsangdo',
        layerNames: ['ne:imsangdo_part1', 'ne:imsangdo_part2', 'ne:imsangdo_part3'],
        url: 'http://localhost:8080/geoserver/ne/wms', // GeoServer 주소는 환경에 맞게 확인 필요
        visible: false, isCollapsibleLegend: true, defaultCollapsed: true,
        colorMap: imsangdoColorMap, codeDescriptions: imsangdoCodeDescriptions,
        filterAttribute: 'FRTP_CD',
    },
    // --- Vector 레이어들 ---
    {
        name: '등산로', type: 'hiking_trail',
        url: '/merged_hiking_trails.geojson', // public 폴더 기준
        visible: false, isCollapsibleLegend: false,
        legendInfo: hikingTrailLegendInfo,
    },
    {
        name: '산악기상관측소 마커', type: 'mountain_station_markers',
        visible: true, isCollapsibleLegend: false,
        legendInfo: mountainMarkerLegendInfo,
    },
    {
        name: '아산천안 연료강도',
        type: 'fuel_strength_display_vector',
        url: 'http://localhost:3001/api/fueldata/asancheonan',
        visible: false,
        isCollapsibleLegend: true,
        defaultCollapsed: true,
        legendInfo: {
            title: '연료 강도 (아산/천안)',
            type: 'colormap_fuel_strength', 
            colors: fuelStrengthColorMap, 
            description: '각 지점의 고유 연료 강도(total_fuel_strength)를 나타냅니다.'
        },
    },
    {
        name: '산불 확산 시뮬레이션',
        type: 'fire_prediction_vector',
        url: 'http://localhost:3001/api/fire-predict-points',
        visible: true,
        isCollapsibleLegend: true,
        defaultCollapsed: false,
        legendInfo: {
            title: '산불 확산 예측 결과',
            type: 'colormap_prediction_danger', 
            colors: { 
                0: 'rgba(0, 255, 0, 0.7)', 1: 'rgba(255, 255, 0, 0.7)', 2: 'rgba(255, 165, 0, 0.7)',
                3: 'rgba(255, 0, 0, 0.7)', 4: 'rgba(0, 0, 0, 0.9)'
            },
            description: '예측된 산불 확산 위험도입니다. 클릭하여 발화점을 선택하세요.'
        },
    },
    { 
        name: '동료 DB 격자 데이터', // 레이어 이름 변경
        type: 'mapped_grid_data_vector', 
        // ⭐ API 엔드포인트를 동료 DB를 사용하는 주소로 변경합니다.
        url: 'http://localhost:3001/api/colleague-grid-data', 
        visible: true, 
        isCollapsibleLegend: true,
        defaultCollapsed: false,
        legendInfo: {
            title: '동료 DB 격자 데이터', // 범례 제목 수정
            type: 'simple_point_legend', 
            description: '동료의 외부 DB에서 가져온 격자 지점입니다.', // 범례 설명 수정
            style: { 
                color: 'rgba(0, 0, 255, 0.6)', // 색상을 다르게 하여 구분 (예: 파란색)
                radius: 3
            }
        },
    }
];
