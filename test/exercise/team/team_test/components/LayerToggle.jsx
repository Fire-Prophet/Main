import React from 'react';

const LayerToggleButton = ({ label, active, onClick }) => (
  <button
    onClick={onClick}
    style={{
      margin: '5px',
      padding: '8px 14px',
      borderRadius: '6px',
      backgroundColor: active ? '#B33E2C' : '#ccc',
      color: 'white',
      border: 'none',
      cursor: 'pointer'
    }}
  >
    {label}
  </button>
);

export default LayerToggleButton;
