import geopandas as gpd
import numpy as np
from rasterio.features import rasterize
from model.label import storunst_map, forest_type_map, species_group_map, diameter_class_map, age_class_map, density_code_map, height_class_map
from model.ca_base import CAModel
import os
import matplotlib.pyplot as plt
import argparse

# python ca_anderson13_demo.py --steps 100 --ignite_x 30 --ignite_y 40 --tree_density 0.8 --result_dir my_results
# 이 코드는 Anderson13 연료모델을 기반으로 한 CA 시뮬레이션을 수행합니다.
# 주요 단계는 다음과 같습니다:


# 1. SHP 파일 로드 및 Anderson13 연료모델 벡터화
def load_and_vectorize_shp(shp_path):
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
    idx2code = {i:c for i,c in enumerate(anderson13_codes)}
    gdf['FuelIdx'] = gdf['Anderson13_FuelModel'].map(code2idx).fillna(0).astype(int)
    # fuel_array를 코드로 변환
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
    fuel_code_map = np.vectorize(idx2code.get)(fuel_array)

    return gdf, fuel_array, fuel_code_map

# 4. Anderson13 코드별 번짐확률 예시
def get_fuel_spread_probs():
    return {
        'TL1': 0.10, 'TL2': 0.12, 'TL3': 0.13, 'TU1': 0.18, 'TU2': 0.20, 'TU3': 0.22, 'TU4': 0.20, 'TU5': 0.25,
        'GS1': 0.30, 'GR1': 0.35, 'SH1': 0.28, 'NB1': 0.01
    }

def parse_args():
    parser = argparse.ArgumentParser(description='Anderson13 기반 CA 시뮬레이션')
    parser.add_argument('--shp_path', type=str, default='model/44200/44200.shp', help='Shapefile 경로')
    parser.add_argument('--result_dir', type=str, default='ca_results', help='결과 저장 폴더')
    parser.add_argument('--steps', type=int, default=50, help='시뮬레이션 스텝 수')
    parser.add_argument('--ignite_x', type=int, default=None, help='점화 x좌표 (기본: 중앙)')
    parser.add_argument('--ignite_y', type=int, default=None, help='점화 y좌표 (기본: 중앙)')
    parser.add_argument('--tree_density', type=float, default=0.7, help='초기 나무 밀도')
    parser.add_argument('--p_ignite', type=float, default=0.0005, help='자연발화 확률')
    parser.add_argument('--save_interval', type=int, default=10, help='이미지 저장 주기')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    shp_path = args.shp_path
    result_dir = args.result_dir
    steps = args.steps
    tree_density = args.tree_density
    p_ignite = args.p_ignite
    save_interval = args.save_interval

    gdf, fuel_array, fuel_code_map = load_and_vectorize_shp(shp_path)

    fuel_spread_probs = get_fuel_spread_probs()

    # 5. CA 모델 생성 및 실행
    ca = CAModel(
        grid_shape=fuel_array.shape,
        n_states=3,
        p_ignite=p_ignite,
        seed=42,
        fuel_map=fuel_code_map,
        fuel_spread_probs=fuel_spread_probs
    )
    ca.initialize(tree_density=tree_density)

    # 점화 위치 지정
    ignite_x = args.ignite_x if args.ignite_x is not None else fuel_array.shape[0]//2
    ignite_y = args.ignite_y if args.ignite_y is not None else fuel_array.shape[1]//2
    ca.ignite(ignite_x, ignite_y)

    os.makedirs(result_dir, exist_ok=True)
    for i in range(steps):
        ca.step()
        np.save(os.path.join(result_dir, f'step_{i:03d}.npy'), ca.grid)
        if i % save_interval == 0 or i == steps-1:
            plt.imshow(ca.grid, cmap='hot', interpolation='nearest')
            plt.title(f'CA Step {i}')
            plt.axis('off')
            plt.savefig(os.path.join(result_dir, f'step_{i:03d}.png'), bbox_inches='tight')
            plt.close()
