export async function fetchWeather(areaCode) {
  const res = await fetch(`https://api.example.com/weather/${areaCode}`);
  if (!res.ok) throw new Error('날씨 데이터를 불러올 수 없습니다');
  return await res.json();
}
