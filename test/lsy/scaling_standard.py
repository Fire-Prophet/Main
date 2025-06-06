import pandas as pd
from sklearn.preprocessing import StandardScaler

#  CSV 파일 불러오기
df = pd.read_csv('Car price prediction(used cars).csv', encoding='ISO-8859-1')

#  전처리 예시 (스케일링이 가능한 상태로 만들기)
df['Levy'] = df['Levy'].replace('-', '0').str.replace(',', '').astype(float)
df['Mileage'] = df['Mileage'].str.replace(' km', '').str.replace(',', '').astype(float)
df['Prod. year'] = pd.to_numeric(df['Prod. year'], errors='coerce')
df['Cylinders'] = pd.to_numeric(df['Cylinders'], errors='coerce')
df['Engine volume'] = df['Engine volume'].astype(str).str.replace('Turbo', '').str.strip()
df['Engine volume'] = pd.to_numeric(df['Engine volume'], errors='coerce')

# 스케일링할 수치형 컬럼
numeric_cols = ['Levy', 'Mileage', 'Engine volume', 'Cylinders', 'Prod. year']

# StandardScaler 적용
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df[numeric_cols])
scaled_df = pd.DataFrame(scaled_data, columns=[f"{col}_scaled" for col in numeric_cols])

# 기존 df에 정규화된 컬럼 추가
df = pd.concat([df, scaled_df], axis=1)

# 결과 확인
print(df[[f"{col}_scaled" for col in numeric_cols]].head())
print("정규화 완료!")
