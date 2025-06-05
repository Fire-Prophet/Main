CREATE TABLE predictions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  region VARCHAR(50),
  temp FLOAT,
  humidity FLOAT,
  wind FLOAT,
  risk_level VARCHAR(10),
  predicted_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
