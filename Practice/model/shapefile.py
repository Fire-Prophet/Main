import geopandas as gpd

# 1) 임상도 SHP 파일 경로 지정
shp_path = "/44200/44200.shp"

# 2) GeoDataFrame으로 불러오기
gdf = gpd.read_file(shp_path)

# 3) CRS(좌표계)·칼럼·샘플 데이터 확인
print("CRS:", gdf.crs)
print("컬럼 목록:", gdf.columns.tolist())
print(gdf.head(3))
# 예: ['STORUNST_CD','FROR_CD','FRTP_CD','KOFTR_GROU_CD', … ]