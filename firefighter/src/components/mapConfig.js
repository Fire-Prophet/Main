import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';
import Circle from 'ol/style/Circle';
// Icon import는 fireStartMarkerStyle 에서 사용했었으나, 현재 VWorldMap.js에서 직접 사용하지 않으므로 주석 처리 또는 필요시 추가
// import Icon from 'ol/style/Icon';

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

// --- 경상북도 토양도 범례 정보 ---
export const gyeongbukSoilColorMap = {
    '01': '#774fd3', '02': '#e26448', '03': '#bd59ef', '04': '#52cf58',
    '05': '#4dda8a', '06': '#48bed9', '07': '#c321dc', '08': '#108ed7',
    '10': '#56d31c', '11': '#f02ac2', '12': '#d550ce', '13': '#78d21e',
    '14': '#56e8cb', '15': '#ddd55e', '16': '#eeba1d', '17': '#7b81d4',
    '18': '#bfd22e', '19': '#9f6fd3', '24': '#47db6c', '25': '#7293ed',
    '26': '#ef7f7f', '27': '#90cb10', '28': '#2acb8d', '29': '#ea1a43',
    '82': '#523ee9', '91': '#cd9041', '92': '#61d54f', '93': '#d00f7f',
    '94': '#729dd1', '95': '#3be7e4', '99': '#cb7a4b',
};
export const gyeongbukSoilCodeDescriptions = {
    '01': '갈색건조산림토양(1)', '02': '갈색약건산림토양(2)', /* ... (나머지 경북 토양 설명 전체 복사) ... */
    '03': '갈색적윤산림토양(3)', '04': '갈색약습산림토양(4)', '05': '적색계갈색건조산림토양(5)',
    '06': '적색계갈색약건산림토양(6)', '07': '적색건조산림토양(7)', '08': '적색약건산림토양(8)',
    '10': '암적색건조산림토양(10)', '11': '암적색약건산림토양(11)', '12': '암적색적윤산림토양(12)',
    '13': '암적갈색건조산림토양(13)', '14': '암적갈색약건산림토양(14)', '15': '회갈색건조산림토양(15)',
    '16': '회갈색약건산림토양(16)', '17': '화산회건조산림토양(17)', '18': '화산회약건산림토양(18)',
    '19': '화산회적윤산림토양(19)', '24': '약침식토양(24)', '25': '강침식토양(25)',
    '26': '사방지토양(26)', '27': '미숙토양(27)', '28': '암쇄토양(28)', '29': '전석지(29)',
    '82': '제지(R)', '91': '주거지(S)', '92': '초지(G)', '93': '경작지(C)',
    '94': '수채(W)', '95': '과수원(O)', '99': '기타(E)',
};

// --- 임상도 범례 정보 ---
export const imsangdoColorMap = {
    '0': '#D2B48C', '1': '#38A800', '2': '#B370D7', '3': '#34CA96', '4': '#A1DDA1',
};
export const imsangdoCodeDescriptions = {
    '0': '무립목지 / 비산림', '1': '침엽수림 (수관 75% 이상)',
    '2': '활엽수림 (수관 75% 이상)', '3': '혼효림 (침엽 25~75%)', '4': '죽림',
};

// --- "아산천안 연료 강도" 표시용 색상 정의 (VWorldMap.js의 fuelDisplayPointStyleFunction 에서 사용) ---
export const fuelStrengthColorMap = { // 이전에 fuelStrengthColorMap으로 사용되었던 것과 유사한 개념
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

// --- 산불 시작점 마커 스타일 (현재 VWorldMap.js에서는 직접 사용하지 않으나, 필요시 활용 가능) ---
// export const fireStartMarkerStyle = new Style({ /* ... 이전 코드 ... */ });


// --- 논리적인 레이어 그룹 설정 ---
export const logicalLayersConfig = [
    // --- WMS 레이어들 ---
    {
        name: '아산천안 토양', type: 'soil',
        layerNames: ['ne:Asan_Cheonan_Soil_1', 'ne:Asan_Cheonan_Soil_2', 'ne:Asan_Cheonan_Soil_3'],
        url: 'http://localhost:8080/geoserver/ne/wms', 
        visible: false, isCollapsibleLegend: true, defaultCollapsed: true,
        colorMap: asanCheonanSoilColorMap, codeDescriptions: asanCheonanSoilCodeDescriptions,
        filterAttribute: 'SLTP_CD',
    },
    {
        name: '경상북도 토양도', type: 'soil',
        layerNames: ['ne:gyeongbuk_soil'], url: 'http://localhost:8080/geoserver/ne/wms',
        visible: false, isCollapsibleLegend: true, defaultCollapsed: true,
        colorMap: gyeongbukSoilColorMap, codeDescriptions: gyeongbukSoilCodeDescriptions,
        filterAttribute: 'SLTP_CD',
    },
    {
        name: '아산천안 임상도', type: 'imsangdo',
        layerNames: ['ne:imsangdo_part1', 'ne:imsangdo_part2', 'ne:imsangdo_part3'],
        url: 'http://localhost:8080/geoserver/ne/wms', 
        visible: false, isCollapsibleLegend: true, defaultCollapsed: true,
        colorMap: imsangdoColorMap, codeDescriptions: imsangdoCodeDescriptions,
        filterAttribute: 'FRTP_CD',
    },
    {
        name: '경상북도 임상도', type: 'imsangdo',
        layerNames: ['ne:gyeongbuk_forest'], url: 'http://localhost:8080/geoserver/ne/wms',
        visible: false, isCollapsibleLegend: true, defaultCollapsed: true,
        colorMap: imsangdoColorMap, codeDescriptions: imsangdoCodeDescriptions,
        filterAttribute: 'FRTP_CD',
    },
    // --- Vector 레이어들 ---
    {
        name: '등산로', type: 'hiking_trail',
        fileUrls: ['/merged_hiking_trails.geojson'], // public 폴더 기준 경로
        visible: false, isCollapsibleLegend: false,
        legendInfo: hikingTrailLegendInfo,
    },
    {
        name: '산악기상관측소 마커', type: 'mountain_station_markers',
        visible: true, isCollapsibleLegend: false, 
        legendInfo: mountainMarkerLegendInfo,
    },
    { // ⭐ 레이어 1: 실제 연료 강도 표시용 (아산/천안 지역)
        name: '아산천안 연료강도', 
        type: 'fuel_strength_display_vector', // VWorldMap.js에서 이 타입으로 식별
        url: 'http://localhost:3001/api/fueldata/asancheonan', // fuel_data_asan_cheonan 테이블 데이터 API
        visible: false, // 초기에는 숨김 (사용자가 선택적으로 켤 수 있도록)
        isCollapsibleLegend: true, 
        defaultCollapsed: true,
        legendInfo: {
            title: '연료 강도 (아산/천안)',
            type: 'colormap_fuel_strength', // Legend.js에서 이 타입에 맞는 범례를 표시하도록 구현 필요
            colors: fuelStrengthColorMap, // 위에서 정의한 fuelStrengthColorMap 사용
            description: '각 지점의 고유 연료 강도(total_fuel_strength)를 나타냅니다.'
        },
    },
    { // ⭐ 레이어 2: 산불 확산 시뮬레이션용
        name: '산불 확산 시뮬레이션', 
        type: 'fire_prediction_vector', // VWorldMap.js에서 이 타입으로 식별
        url: 'http://localhost:3001/api/fire-predict-points', // fire_predict_points 테이블 데이터 API
        visible: true, // 시뮬레이션을 위해 기본적으로 보이도록 설정
        isCollapsibleLegend: true, 
        defaultCollapsed: false,
        legendInfo: {
            title: '산불 확산 예측 결과',
            type: 'colormap_prediction_danger', // Legend.js에서 이 타입에 맞는 범례를 표시하도록 구현 필요
            // VWorldMap.js에서 dangerLevelColors 객체를 직접 사용하여 스타일링하므로,
            // 범례에도 이 색상 정보를 전달하거나, Legend.js에서 직접 정의하여 사용 가능
            colors: { // VWorldMap.js의 dangerLevelColors와 일치 또는 참조
                0: '안전 (초록)', 1: '주의 (노랑)', 2: '위험 (주황)', 3: '매우 위험 (빨강)', 4: '발화점 (검정)'
            },
            description: '예측된 산불 확산 위험도입니다. 클릭하여 발화점을 선택하세요.'
        },
    }
];