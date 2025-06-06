import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.family'] = 'Malgun Gothic'  # 윈도우 기본 한글 폰트
plt.rcParams['axes.unicode_minus'] = False

# CSV 불러오기
df = pd.read_csv('Car price prediction(used cars).csv', encoding='ISO-8859-1')

# 전처리
df = df[df['Prod. year'].str.isnumeric()].copy()
df['Levy'] = df['Levy'].replace('-', '0').str.replace(',', '').astype(float)
df['Mileage'] = df['Mileage'].str.replace(' km', '').str.replace(',', '').astype(float)
df['Prod. year'] = df['Prod. year'].astype(int)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df['Cylinders'] = pd.to_numeric(df['Cylinders'], errors='coerce')
df['Engine volume'] = df['Engine volume'].astype(str).str.replace('Turbo', '').str.strip()
df['Engine volume'] = pd.to_numeric(df['Engine volume'], errors='coerce')
df['Fuel type'] = df['Fuel type'].astype(str)

# 이상치 제거 (Price, Mileage 기준 IQR 방식)
Q1_price = df['Price'].quantile(0.25)
Q3_price = df['Price'].quantile(0.75)
IQR_price = Q3_price - Q1_price

Q1_mileage = df['Mileage'].quantile(0.25)
Q3_mileage = df['Mileage'].quantile(0.75)
IQR_mileage = Q3_mileage - Q1_mileage

df = df[
    (df['Price'] >= Q1_price - 1.5 * IQR_price) & (df['Price'] <= Q3_price + 1.5 * IQR_price) &
    (df['Mileage'] >= Q1_mileage - 1.5 * IQR_mileage) & (df['Mileage'] <= Q3_mileage + 1.5 * IQR_mileage)
]

# 2x2 subplot 생성
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Cylinders vs Levy
sns.scatterplot(x='Cylinders', y='Levy', data=df, ax=axes[0, 0])
axes[0, 0].set_title('Cylinders vs Levy')

# Mileage vs Price
sns.scatterplot(x='Mileage', y='Price', data=df, ax=axes[0, 1],alpha=0.2, s=10)
axes[0, 1].set_title('Mileage vs Price')

# 연식별 평균 가격 선 그래프
year_price = df.groupby('Prod. year')['Price'].mean().reset_index()
sns.lineplot(x='Prod. year', y='Price', data=year_price, ax=axes[1, 0])
axes[1, 0].set_title('연식에 따른 평균 중고차 가격')

# Fuel type vs Price
sns.boxplot(x='Fuel type', y='Price', data=df, ax=axes[1, 1])
axes[1, 1].set_title('Fuel type vs Price')
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()
