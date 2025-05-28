import React from 'react';

const DateSelector = ({ value, onChange }) => (
  <input
    type="date"
    value={value}
    onChange={(e) => onChange(e.target.value)}
    style={{ padding: '8px', margin: '10px 0', borderRadius: '5px' }}
  />
);

export default DateSelector;
