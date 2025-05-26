import geopandas as gpd
import numpy as np
from rasterio.features import rasterize
from model.label import storunst_map, forest_type_map, species_group_map, diameter_class_map, age_class_map, density_code_map, height_class_map
from model.ca_base import CAModel
import os
import matplotlib.pyplot as plt

# 1. SHP 파일 로드 및 Anderson13 연료모델 벡터화
shp_path = "model/44200/44200.shp"
gdf = gpd.read_file(shp_path)
gdf['STORUNST_CD'] = gdf['STORUNST_CD'].astype(str).str.zfill(1)
gdf['HEIGT_CD'] = gdf['HEIGT_CD'].astype(str).str.zfill(2)

conds = [
    (gdf['STORUNST_CD'].isin(['0','2'])) | (gdf['FRTP_CD']=='0'),
    (gdf['STORUNST_CD']=='1') & (gdf['FRTP_CD']=='1') & (gdf['DNST_CD']=='C') & (gdf['HEIGT_CD'].astype(int) >= 20),
    (gdf['STORUNST_CD']=='1') & (gdf['FRTP_CD']=='1') & (gdf['DNST_CD'].isin(['B','C'])),
    (gdf['STORUNST_CD']=='1') & (gdf['FRTP_CD']=='1'),
    (gdf['STORUNST_CD']=='1') & (gdf['FRTP_CD']=='2') & (gdf['DNST_CD']=='C') & (gdf['HEIGT_CD'].astype(int) >= 20),
    (gdf['STORUNST_CD']=='1') & (gdf['FRTP_CD']=='2') & (gdf['DNST_CD'].isin(['B','C'])),
    (gdf['STORUNST_CD']=='1') & (gdf['FRTP_CD']=='2'),
    (gdf['STORUNST_CD']=='1') & (gdf['FRTP_CD']=='3') & (gdf['DNST_CD']=='C'),
    (gdf['STORUNST_CD']=='1') & (gdf['FRTP_CD']=='3'),
    (gdf['STORUNST_CD']=='1') & (gdf['FRTP_CD']=='4'),
    (gdf['KOFTR_GROU_CD']=='92'),
    (gdf['KOFTR_GROU_CD']=='83'),
    (gdf['KOFTR_GROU_CD'].isin(['91','93','94','95','99'])),
]
choices = [
    'NB1', 'TU1', 'TU2', 'TL1', 'TU3', 'TU4', 'TL2', 'TU5', 'TL3', 'GS1', 'GR1', 'SH1', 'NB1'
]
gdf['Anderson13_FuelModel'] = np.select(conds, choices, default='TL1')

# 2. Anderson13 연료코드를 숫자 인덱스로 변환 (CA용)
anderson13_codes = ['TL1','TL2','TL3','TU1','TU2','TU3','TU4','TU5','GS1','GR1','SH1','NB1']
code2idx = {c:i for i,c in enumerate(anderson13_codes)}
gdf['FuelIdx'] = gdf['Anderson13_FuelModel'].map(code2idx).fillna(0).astype(int)

# 3. Rasterize: 연료 인덱스 맵 만들기 (격자 해상도 30m)
from rasterio.transform import from_origin
minx, miny, maxx, maxy = gdf.total_bounds
xres = yres = 30
width = int((maxx-minx)/xres)+1
height = int((maxy-miny)/yres)+1
transform = from_origin(minx, maxy, xres, yres)
fuel_array = rasterize(
    [(geom, idx) for geom, idx in zip(gdf.geometry, gdf['FuelIdx'])],
    out_shape=(height, width),
    transform=transform,
    fill=0,
    dtype='int32'
)

# 4. Anderson13 코드별 번짐확률 예시
fuel_spread_probs = {
    'TL1': 0.10, 'TL2': 0.12, 'TL3': 0.13, 'TU1': 0.18, 'TU2': 0.20, 'TU3': 0.22, 'TU4': 0.20, 'TU5': 0.25,
    'GS1': 0.30, 'GR1': 0.35, 'SH1': 0.28, 'NB1': 0.01
}
# fuel_array를 코드로 변환
idx2code = {i:c for c,i in code2idx.items()}
fuel_code_map = np.vectorize(idx2code.get)(fuel_array)

# 5. CA 모델 생성 및 실행
ca = CAModel(
    grid_shape=fuel_array.shape,
    n_states=3,
    p_ignite=0.0005,
    seed=42,
    fuel_map=fuel_code_map,
    fuel_spread_probs=fuel_spread_probs
)
ca.initialize(tree_density=0.7)
ca.ignite(fuel_array.shape[0]//2, fuel_array.shape[1]//2)

# 결과 저장 폴더
result_dir = 'ca_results'
os.makedirs(result_dir, exist_ok=True)

# 시뮬레이션 및 저장
for i in range(50):
    ca.step()
    # 상태 저장 (npy)
    np.save(os.path.join(result_dir, f'step_{i:03d}.npy'), ca.grid)
    # 이미지 저장 (png)
    if i % 10 == 0 or i == 49:
        plt.imshow(ca.grid, cmap='hot', interpolation='nearest')
        plt.title(f'CA Step {i}')
        plt.axis('off')
        plt.savefig(os.path.join(result_dir, f'step_{i:03d}.png'), bbox_inches='tight')
        plt.close()
