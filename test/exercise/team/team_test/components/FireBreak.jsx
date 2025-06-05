import React from 'react';

const FireBreakInfo = ({ fireBreaks }) => (
  <div>
    <h3>방화선 정보</h3>
    <ul>
      {fireBreaks.map((line, i) => (
        <li key={i}>{line.name} - 길이: {line.length}m</li>
      ))}
    </ul>
  </div>
);

export default FireBreakInfo;
