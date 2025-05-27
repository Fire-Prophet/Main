import React from 'react';
import { useNavigate } from 'react-router-dom';

const StartButton = () => {
  const navigate = useNavigate();
  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <button
        onClick={() => navigate('/map')}
        style={{
          backgroundColor: '#B33E2C',
          color: 'white',
          fontSize: '1.2rem',
          padding: '12px 24px',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer'
        }}
      >
        시작하기
      </button>
    </div>
  );
};

export default StartButton;
