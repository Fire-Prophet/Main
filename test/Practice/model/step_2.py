import geopandas as gpd
import numpy as np
from model.label import storunst_map, forest_type_map, species_group_map, diameter_class_map, age_class_map, density_code_map, height_class_map

# 1) 임상도 SHP 파일 경로 지정
shp_path = "model/44200/44200.shp"

# 2) GeoDataFrame으로 불러오기
gdf = gpd.read_file(shp_path)

# 3) 코드 문자열 통일
gdf['STORUNST_CD'] = gdf['STORUNST_CD'].astype(str).str.zfill(1)
gdf['HEIGT_CD'] = gdf['HEIGT_CD'].astype(str).str.zfill(2)

# 4) 기본 맵핑 + 결측치 처리
gdf['Storunst'] = gdf['STORUNST_CD'].map(storunst_map).fillna('알수없음')
gdf["ForestType"] = gdf["FRTP_CD"].map(forest_type_map)
gdf["Species"] = gdf["KOFTR_GROU_CD"].map(species_group_map)
gdf["DiaClass"] = gdf["DMCLS_CD"].map(diameter_class_map)
gdf["AgeClass"] = gdf["AGCLS_CD"].map(age_class_map)
gdf["Density"] = gdf["DNST_CD"].map(density_code_map)
gdf["HeightClass"] = gdf["HEIGT_CD"].map(height_class_map)

# 5) np.select 기반 Anderson13 벡터화 매핑
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
    'NB1',  # 비산림/무립목지
    'TU1',  # 침엽수림, 밀도 높고 키 큼
    'TU2',  # 침엽수림, 밀도 중/높음
    'TL1',  # 침엽수림, 그 외
    'TU3',  # 활엽수림, 밀도 높고 키 큼
    'TU4',  # 활엽수림, 밀도 중/높음
    'TL2',  # 활엽수림, 그 외
    'TU5',  # 혼효림, 밀도 높음
    'TL3',  # 혼효림, 그 외
    'GS1',  # 죽림
    'GR1',  # 초지
    'SH1',  # 관목덤불
    'NB1',  # 기타 비산림
]
gdf['Anderson13_FuelModel'] = np.select(conds, choices, default='TL1')

# 6) 결과 확인
gdf.head().to_csv('sample_labeled.csv', index=False)
print(gdf.head())
print('라벨링 및 Anderson13 매핑 완료!')
