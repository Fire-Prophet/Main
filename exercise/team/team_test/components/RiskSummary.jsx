import React from 'react';

const RiskSummaryCard = ({ total, avgRisk }) => (
  <div style={{
    background: '#fff', padding: '10px 16px',
    border: '1px solid #ccc', borderRadius: '8px', margin: '12px 0'
  }}>
    <h4>통합 요약</h4>
    <p>분석 지역 수: {total}개</p>
    <p>평균 위험도: <strong>{avgRisk}</strong></p>
  </div>
);

export default RiskSummaryCard;
