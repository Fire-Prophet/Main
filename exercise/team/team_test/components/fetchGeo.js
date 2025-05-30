export async function fetchGeoJSON(layerName) {
  const response = await fetch(`/api/layers/${layerName}`);
  if (!response.ok) throw new Error('GeoJSON 데이터 로드 실패');
  return await response.json();
}
