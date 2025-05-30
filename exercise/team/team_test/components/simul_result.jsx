import React from 'react';

const FireSimulationResult = ({ data }) => (
  <div>
    <h2>예측 결과</h2>
    {data.map((d, i) => (
      <div key={i}>
        <strong>{d.area}</strong>: {d.risk}
      </div>
    ))}
  </div>
);

export default FireSimulationResult;
