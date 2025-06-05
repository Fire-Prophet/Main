const turf = require('@turf/turf');

exports.getNearestShelter = (userPoint, shelterList) => {
  const from = turf.point(userPoint);
  const options = { units: 'kilometers' };
  let nearest = null, min = Infinity;

  shelterList.forEach(shelter => {
    const dist = turf.distance(from, turf.point(shelter.coords), options);
    if (dist < min) {
      min = dist;
      nearest = shelter;
    }
  });

  return nearest;
};
