const axios = require('axios');

exports.proxyWMS = async (req, res) => {
  const wmsUrl = `http://your-geoserver/wms?${req.queryString}`;
  try {
    const result = await axios.get(wmsUrl, { responseType: 'arraybuffer' });
    res.set('Content-Type', 'image/png');
    res.send(result.data);
  } catch (e) {
    res.status(500).send('WMS 요청 실패');
  }
};
