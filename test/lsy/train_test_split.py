import pandas as pd
from sklearn.model_selection import train_test_split

# 데이터 불러오기
df = pd.read_csv('Car price prediction(used cars).csv', encoding='ISO-8859-1')

# 전처리
df = df[df['Prod. year'].str.isnumeric()].copy()
df['Levy'] = df['Levy'].replace('-', '0').str.replace(',', '').astype(float)
df['Mileage'] = df['Mileage'].str.replace(' km', '').str.replace(',', '').astype(float)
df['Prod. year'] = df['Prod. year'].astype(int)
df['Cylinders'] = pd.to_numeric(df['Cylinders'], errors='coerce')
df['Turbo'] = df['Turbo'] = df['Engine volume'].apply(lambda x: 1 if isinstance(x, str) and 'Turbo' in x else 0)
df['Engine volume'] = df['Engine volume'].astype(str).str.replace('Turbo', '').str.strip()
df['Engine volume'] = pd.to_numeric(df['Engine volume'], errors='coerce')


# 결측값 제거
df = df[['Prod. year', 'Mileage', 'Engine volume', 'Cylinders', 'Turbo', 'Price']].dropna()

# 데이터 분할
X = df[['Prod. year', 'Mileage', 'Engine volume', 'Cylinders', 'Turbo']]
y = df['Price']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("학습용 데이터 크기:", X_train.shape)
print("테스트용 데이터 크기:", X_test.shape)
