# 1_setup_data.py

import numpy as np
import pandas as pd

# 간단한 학습용 데이터 (온도, 습도, 풍속 → 위험도)
data = {
    'temp': [33, 30, 27, 25, 22, 19],
    'humidity': [15, 30, 40, 50, 60, 70],
    'wind': [7, 5, 4, 3, 2, 1],
    'risk_level': [3, 2, 2, 1, 0, 0]  # 0: 낮음 ~ 3: 위험
}

df = pd.DataFrame(data)
df.to_csv('fire_data.csv', index=False)
