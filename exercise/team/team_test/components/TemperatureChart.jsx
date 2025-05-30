import React from 'react';
import { Line } from 'react-chartjs-2';

const TemperatureChart = ({ data }) => {
  const chartData = {
    labels: data.map(d => d.time),
    datasets: [{
      label: '온도(℃)',
      data: data.map(d => d.temp),
      borderColor: '#B33E2C',
      fill: false
    }]
  };

  return <Line data={chartData} />;
};

export default TemperatureChart;
