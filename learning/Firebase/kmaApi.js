const axios = require('axios');

const KMA_API_KEY = 'q1XWOAcb5VskyP5OQGl%2B08hLR9MyROzs%2Fav5AbVDjLpvMEbcl4qlFU%2BxSf6oxNDm2XGu0ljXk6cjUocIPX7N8Q%3D%3D';
const KMA_WEATHER_API_URL = 'http://apis.data.go.kr/1400377/mtweather/mountListSearch';

async function fetchKmaWeatherData(obsid, requestTm) {
    const queryParams = `?serviceKey=${KMA_API_KEY}&pageNo=1&numOfRows=1&_type=json&obsid=${encodeURIComponent(obsid)}&tm=${encodeURIComponent(requestTm)}`;
    try {
        console.log(`[기상청 API] obsid: ${obsid}, 시간: ${requestTm} 날씨 정보 요청 중...`);
        const response = await axios.get(KMA_WEATHER_API_URL + queryParams, { timeout: 15000 });

        if (response.data?.response?.header?.resultCode === "00") {
            const items = response.data.response.body?.items?.item;
            return Array.isArray(items) ? items[0] : items;
        } else {
            console.error(`[기상청 API] obsid: ${obsid} API 오류 발생:`, response.data?.response?.header?.resultMsg);
            return null;
        }
    } catch (error) {
        console.error(`[기상청 API] obsid: ${obsid} 요청 실패:`, error.message);
        return null;
    }
}

module.exports = fetchKmaWeatherData;
