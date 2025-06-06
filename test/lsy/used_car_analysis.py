import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.family'] = 'Malgun Gothic'  # 윈도우 기본 한글 폰트
plt.rcParams['axes.unicode_minus'] = False

df_raw = pd.read_csv('Car price prediction(used cars).csv', encoding='ISO-8859-1')
df = df_raw.copy()  # 기존처럼 df 사용


# CSV 불러오기
df = pd.read_csv('Car price prediction(used cars).csv', encoding='ISO-8859-1')

# 비정상 행 제거
df = df[df['Prod. year'].str.isnumeric()].copy()

# 전처리
df['Levy'] = df['Levy'].replace('-', '0').str.replace(',', '').astype(float)
df['Mileage'] = df['Mileage'].str.replace(' km', '').str.replace(',', '').astype(float)
df['Prod. year'] = df['Prod. year'].astype(int)
df['Doors'] = df['Doors'].replace('04-May', 4)
df['Doors'] = pd.to_numeric(df['Doors'], errors='coerce')
df['Cylinders'] = pd.to_numeric(df['Cylinders'], errors='coerce')

# Engine volume 처리: Turbo 여부 분리
df['Turbo'] = df['Engine volume'].apply(lambda x: 1 if isinstance(x, str) and 'Turbo' in x else 0)
df['Engine volume'] = df['Engine volume'].astype(str).str.replace('Turbo', '').str.strip()
df['Engine volume'] = pd.to_numeric(df['Engine volume'], errors='coerce')

# 히트맵을 위한 수치형 변수
numeric_cols = ['Price', 'Levy', 'Prod. year', 'Engine volume', 'Mileage',
                'Cylinders', 'Airbags', 'Turbo']

# 결측값 제거 후 상관관계 히트맵
df_corr = df[numeric_cols].dropna()

plt.figure(figsize=(8, 6))
sns.heatmap(df_corr.corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('수치형 변수 간 상관계수 히트맵')
plt.tight_layout()
plt.show()

# Price 이상치 제거 (IQR 기준)
Q1 = df['Price'].quantile(0.25)
Q3 = df['Price'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df['Price'] >= Q1 - 1.5 * IQR) & (df['Price'] <= Q3 + 1.5 * IQR)]

# 여러 변수에 대한 boxplot (2행 3열 구성)
cols = ['Price', 'Levy', 'Prod. year', 'Engine volume', 'Mileage', 'Cylinders']

plt.figure(figsize=(15, 10))
for i, col in enumerate(cols):
    plt.subplot(2, 3, i+1)
    sns.boxplot(x=df[col])
    plt.title(f'{col}')
plt.tight_layout()
plt.show()

print("초기 관측치 수:", len(df_raw))
print("전처리 후 관측치 수:", len(df))
