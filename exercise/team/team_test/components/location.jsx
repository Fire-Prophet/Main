import React from 'react';

const LocationSelector = ({ selected, onChange }) => {
  const locations = ['아산', '천안', '대전', '광주'];
  return (
    <select value={selected} onChange={e => onChange(e.target.value)}>
      {locations.map(loc => (
        <option key={loc} value={loc}>{loc}</option>
      ))}
    </select>
  );
};

export default LocationSelector;
