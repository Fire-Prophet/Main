exports.getVersion = (req, res) => {
  res.json({
    version: '1.3.0',
    build: '2025-06-02',
    status: 'stable'
  });
};
