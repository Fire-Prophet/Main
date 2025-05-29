export async function predictRisk(temp, humidity, wind) {
  const res = await fetch('http://localhost:5000/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ temp, humidity, wind })
  });
  const data = await res.json();
  return data.risk;
}
