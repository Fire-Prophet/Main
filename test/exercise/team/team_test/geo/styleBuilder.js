exports.buildStyleByRisk = (risk) => {
  const colors = ['#4CAF50', '#FFC107', '#FF5722', '#B71C1C'];
  return {
    fillColor: colors[risk],
    strokeColor: '#000',
    strokeWidth: 1,
    fillOpacity: 0.6
  };
};
