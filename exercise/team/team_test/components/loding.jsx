import React from 'react';

const LoadingSpinner = () => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    marginTop: '50px'
  }}>
    <div className="spinner" />
    <style>{`
      .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #ccc;
        border-top: 4px solid #B33E2C;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `}</style>
  </div>
);

export default LoadingSpinner;
