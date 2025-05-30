// src/App.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { database } from './firebaseConfig';
import { ref, onValue } from "firebase/database";
import './App.css'; // App.css 파일 임포트

// API 서버 주소
const API_URL = 'http://localhost:3001/api/parkinglots';

// --- 주차장 폼 컴포넌트 ---
function ParkingLotForm({ lot, onSubmit, onCancel }) {
  // lot이 있으면 수정 모드, 없으면 추가 모드
  const [formData, setFormData] = useState(
    lot || { Name: '', Address: '', Latitude: '', Longitude: '', TotalSpaces: '', HourlyRate: '' }
  );

  // 입력값 변경 핸들러
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // 폼 제출 핸들러
  const handleSubmit = (e) => {
    e.preventDefault();
    // 부모 컴포넌트에서 받은 onSubmit 함수 호출
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="parking-form">
      <h3>{lot ? `주차장 수정 (ID: ${lot.LotID})` : '새 주차장 추가'}</h3>
      <label>이름: <input type="text" name="Name" placeholder="주차장 이름" value={formData.Name} onChange={handleChange} required /></label>
      <label>주소: <input type="text" name="Address" placeholder="주소" value={formData.Address} onChange={handleChange} required /></label>
      <label>위도: <input type="number" step="0.0000001" name="Latitude" placeholder="위도 (예: 37.497952)" value={formData.Latitude} onChange={handleChange} required /></label>
      <label>경도: <input type="number" step="0.0000001" name="Longitude" placeholder="경도 (예: 127.027621)" value={formData.Longitude} onChange={handleChange} required /></label>
      <label>총 면수: <input type="number" name="TotalSpaces" placeholder="총 주차 면수" value={formData.TotalSpaces} onChange={handleChange} required /></label>
      <label>시간당 요금: <input type="number" name="HourlyRate" placeholder="시간당 요금 (숫자만)" value={formData.HourlyRate} onChange={handleChange} /></label>
      <div className="form-buttons">
          <button type="submit">{lot ? '수정하기' : '추가하기'}</button>
          {/* onCancel 함수가 있으면 취소 버튼 표시 */}
          {onCancel && <button type="button" onClick={onCancel}>취소</button>}
      </div>
    </form>
  );
}

// --- 메인 App 컴포넌트 ---
function App() {
  const [firebaseData, setFirebaseData] = useState(null);
  const [mysqlData, setMysqlData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingLot, setEditingLot] = useState(null); // 수정 중인 주차장 정보
  const [showAddForm, setShowAddForm] = useState(false); // 추가 폼 보이기/숨기기

  // MySQL 데이터 로딩 함수 (useCallback으로 불필요한 재성성 방지)
  const fetchMysqlData = useCallback(async () => {
    setLoading(true); // 로딩 시작
    setError(null); // 이전 오류 초기화
    try {
      const response = await fetch(API_URL);
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || 'API 서버에서 데이터를 가져오는 데 실패했습니다.');
      }
      const data = await response.json();
      setMysqlData(data);
    } catch (err) {
      console.error("MySQL Fetch Error:", err);
      setError("주차장 정보를 불러오는 데 실패했습니다: " + err.message);
      setMysqlData([]);
    } finally {
      // Firebase 로딩 후 최종적으로 false 처리되도록 주석 처리
      // setLoading(false);
    }
  }, []);

  // 컴포넌트 마운트 시 MySQL 데이터 로딩
  useEffect(() => {
    fetchMysqlData();
  }, [fetchMysqlData]);

  // 컴포넌트 마운트 시 Firebase 데이터 로딩 및 실시간 리스닝
  useEffect(() => {
    const parkingStatusRef = ref(database, 'ParkingStatus');
    const unsubscribe = onValue(parkingStatusRef, (snapshot) => {
      setFirebaseData(snapshot.val());
      setLoading(false); // Firebase까지 로드되면 최종 로딩 완료
    }, (err) => {
      console.error("Firebase Read Error:", err);
      setError(prev => prev ? `${prev} / Firebase 오류: ${err.message}` : `Firebase 오류: ${err.message}`);
      setLoading(false);
    });
    // 컴포넌트 언마운트 시 리스너 정리
    return () => unsubscribe();
  }, []);

  // --- CRUD 핸들러 ---
  const handleApiCall = async (url, method, body = null, successMessage) => {
      try {
          const options = {
              method: method,
              headers: { 'Content-Type': 'application/json' },
          };
          if (body) {
              options.body = JSON.stringify(body);
          }
          const response = await fetch(url, options);
          if (!response.ok) {
              const errorData = await response.json();
              throw new Error(errorData.error || `${successMessage} 실패`);
          }
          alert(successMessage);
          return true;
      } catch (err) {
          alert(`${successMessage} 중 오류 발생: ${err.message}`);
          return false;
      }
  };

  const handleAddLot = async (formData) => {
      if (await handleApiCall(API_URL, 'POST', formData, '주차장 추가')) {
          setShowAddForm(false);
          fetchMysqlData();
      }
  };

  const handleUpdateLot = async (formData) => {
      if (await handleApiCall(`${API_URL}/${formData.LotID}`, 'PUT', formData, '주차장 수정')) {
          setEditingLot(null);
          fetchMysqlData();
      }
  };

  const handleDeleteLot = async (lotId) => {
      if (window.confirm(`정말로 ID ${lotId} 주차장을 삭제하시겠습니까?`)) {
          if (await handleApiCall(`${API_URL}/${lotId}`, 'DELETE', null, '주차장 삭제')) {
              fetchMysqlData();
          }
      }
  };

  // --- 렌더링 로직 ---
  const renderParkingLots = () => {
      return mysqlData.map(lot => {
          const fbLotId = `LotID_${lot.LotID}`;
          const fbData = firebaseData ? firebaseData[fbLotId] : null;

          return (
              <div key={lot.LotID} className="parking-lot">
                  <h3>{lot.Name} (ID: {lot.LotID})</h3>
                  <p>주소: {lot.Address}</p>
                  <p>좌표: ({lot.Latitude}, {lot.Longitude})</p>
                  <p>요금: {lot.HourlyRate}원/시간</p>
                  <p>상태: 총 {lot.TotalSpaces}면 /{' '}
                      <strong className={fbData?.AvailableCount > 0 ? 'available' : 'occupied'}>
                          주차 가능: {fbData ? fbData.AvailableCount : '확인중...'}
                      </strong>
                  </p>
                  <div className="lot-actions">
                      <button onClick={() => setEditingLot(lot)}>수정</button>
                      <button className="delete-button" onClick={() => handleDeleteLot(lot.LotID)}>삭제</button>
                  </div>
              </div>
          );
      });
  };

  // --- 최종 JSX 반환 ---
  return (
    <div className="App">
      <h1>실시간 주차장 관리 시스템</h1>

      {loading && <p>데이터를 불러오는 중입니다...</p>}
      {error && <p className="error-message">오류: {error}</p>}

      <div className="form-container">
          {editingLot ? (
              <ParkingLotForm
                  lot={editingLot}
                  onSubmit={handleUpdateLot}
                  onCancel={() => setEditingLot(null)}
              />
          ) : (
              showAddForm ? (
                  <ParkingLotForm
                      onSubmit={handleAddLot}
                      onCancel={() => setShowAddForm(false)}
                  />
              ) : (
                  <button className="add-button" onClick={() => setShowAddForm(true)}>
                    + 새 주차장 추가하기
                  </button>
              )
          )}
      </div>

      <hr />
      <h2>주차장 목록</h2>
      <div className="parking-list">
          {!loading && mysqlData.length > 0 ? (
              renderParkingLots()
          ) : (
              !loading && <p>등록된 주차장 정보가 없습니다.</p>
          )}
      </div>
    </div>
  );
}

export default App;
