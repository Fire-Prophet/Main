import pandas as pd

data = {
    'temp': [33, 30, 27, 25, 22, 19],
    'humidity': [15, 30, 40, 50, 60, 70],
    'wind': [7, 5, 4, 3, 2, 1],
    'risk_level': [3, 2, 2, 1, 0, 0]
}

df = pd.DataFrame(data)
df.to_csv('fire_data.csv', index=False)
