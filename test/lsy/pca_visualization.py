import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
plt.rcParams['font.family'] = 'Malgun Gothic'  # 윈도우 기본 한글 폰트
plt.rcParams['axes.unicode_minus'] = False

# 데이터 불러오기 및 전처리
df = pd.read_csv('Car price prediction(used cars).csv', encoding='ISO-8859-1')
df = df[df['Prod. year'].str.isnumeric()].copy()
df['Levy'] = df['Levy'].replace('-', '0').str.replace(',', '').astype(float)
df['Mileage'] = df['Mileage'].str.replace(' km', '').str.replace(',', '').astype(float)
df['Prod. year'] = df['Prod. year'].astype(int)
df['Cylinders'] = pd.to_numeric(df['Cylinders'], errors='coerce')
df['Turbo'] = df['Engine volume'].apply(lambda x: 1 if isinstance(x, str) and 'Turbo' in x else 0)
df['Engine volume'] = df['Engine volume'].astype(str).str.replace('Turbo', '').str.strip()
df['Engine volume'] = pd.to_numeric(df['Engine volume'], errors='coerce')


# 특성 선택 및 결측값 제거
df = df[['Prod. year', 'Mileage', 'Engine volume', 'Cylinders', 'Turbo']].dropna()
X = df[['Prod. year', 'Mileage', 'Engine volume', 'Cylinders', 'Turbo']]

Q1 = df['Mileage'].quantile(0.25)
Q3 = df['Mileage'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df['Mileage'] >= Q1 - 1.5 * IQR) & (df['Mileage'] <= Q3 + 1.5 * IQR)]

# 스케일링
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# PCA 수행
pca_2d = PCA(n_components=2)
X_pca_2d = pca_2d.fit_transform(X_scaled)

pca_3d = PCA(n_components=3)
X_pca_3d = pca_3d.fit_transform(X_scaled)

# 가로로 배치된 2D + 3D 시각화
fig = plt.figure(figsize=(14, 6))

# 왼쪽 - 2D PCA
ax1 = fig.add_subplot(1, 2, 1)
sns.scatterplot(x=X_pca_2d[:, 0], y=X_pca_2d[:, 1], ax=ax1)
ax1.set_title('PCA 2D 시각화 (PC1 vs PC2)')
ax1.set_xlabel('PC1')
ax1.set_ylabel('PC2')
ax1.grid(True)

# 오른쪽 - 3D PCA
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.scatter(X_pca_3d[:, 0], X_pca_3d[:, 1], X_pca_3d[:, 2], alpha=0.6)
ax2.set_title('PCA 3D 시각화 (PC1, PC2, PC3)')
ax2.set_xlabel('PC1')
ax2.set_ylabel('PC2')
ax2.set_zlabel('PC3')

plt.tight_layout()
plt.show()
