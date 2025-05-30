import React from 'react';

const SatelliteImageViewer = ({ date, url }) => (
  <div style={{ marginTop: '20px' }}>
    <h4>{date} 위성사진</h4>
    <img src={url} alt="Satellite" style={{ width: '100%', borderRadius: '8px' }} />
  </div>
);

export default SatelliteImageViewer;
