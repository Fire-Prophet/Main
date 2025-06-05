import React from 'react';

const FireRiskCard = ({ area, riskLevel }) => {
  const riskColor = {
    낮음: '#4CAF50',
    보통: '#FFC107',
    높음: '#FF5722',
    위험: '#B71C1C'
  }[riskLevel] || '#999';

  return (
    <div style={{
      border: `2px solid ${riskColor}`,
      padding: '12px',
      marginBottom: '8px',
      borderRadius: '6px',
      backgroundColor: '#fff'
    }}>
      <h3>{area}</h3>
      <p>위험도: <strong style={{ color: riskColor }}>{riskLevel}</strong></p>
    </div>
  );
};

export default FireRiskCard;
