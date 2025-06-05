// src/components/VWorldMap/weatherService.js
import { database } from '../firebaseConfig'; // 경로 수정: ../../firebaseConfig -> ../firebaseConfig
import { ref, onValue, off } from 'firebase/database';




/**
 * Firebase Realtime Database로부터 특정 지점의 날씨 정보를 실시간으로 가져옵니다.
 * @param {string} obsid - 관측 지점 번호 (예: '1910')
 * @param {function} callback - 데이터 수신 시 호출될 콜백 함수 (weatherData, error)
 * @returns {function} Firebase 리스너를 해제하는 함수
 */
export const subscribeToStationWeather = (obsid, callback) => {
  // Firebase에 데이터가 저장될 것으로 예상되는 경로
  // 예: /weatherdata/1910
  const weatherDataRef = ref(database, `weatherdata/${obsid}`);

  const listener = onValue(weatherDataRef, (snapshot) => {
    const data = snapshot.val();
    if (data) {
      callback(data, null); // 데이터와 함께 에러는 null
    } else {
      // 데이터가 없을 경우 (초기 상태이거나, 해당 obsid 데이터가 Firebase에 아직 없을 수 있음)
      callback(null, null); // 데이터 없음, 에러도 일단 없음 (또는 특정 에러 객체 전달 가능)
    }
  }, (error) => {
    console.error("Firebase 데이터 수신 오류 (obsid: " + obsid + "):", error);
    callback(null, error); // 에러 객체 전달
  });

  // 리스너 해제 함수 반환
  return () => {
    off(weatherDataRef, 'value', listener);
  };
};