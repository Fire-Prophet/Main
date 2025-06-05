import React from 'react';

const DataDownloadButton = ({ data }) => {
  const handleDownload = () => {
    const csv = data.map(d => `${d.area},${d.risk}`).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'fire_prediction.csv';
    a.click();
  };

  return <button onClick={handleDownload}>CSV 다운로드</button>;
};

export default DataDownloadButton;
