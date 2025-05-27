import React from 'react';

const MapLegend = () => (
  <div style={{
    position: 'absolute',
    right: '10px',
    top: '70px',
    backgroundColor: '#fff',
    padding: '10px',
    border: '1px solid #ccc'
  }}>
    <h4>위험도 범례</h4>
    <ul style={{ listStyle: 'none', padding: 0 }}>
      <li style={{ color: '#4CAF50' }}>■ 낮음</li>
      <li style={{ color: '#FFC107' }}>■ 보통</li>
      <li style={{ color: '#FF5722' }}>■ 높음</li>
      <li style={{ color: '#B71C1C' }}>■ 위험</li>
    </ul>
  </div>
);

export default MapLegend;
