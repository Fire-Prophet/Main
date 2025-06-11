import rasterio
from rasterio.features import rasterize

# 1) 출력격자 해상도, 범위 정의 (예: 30m × 30m)
transform = rasterio.transform.from_origin(xmin, ymax, 30, 30)
out_shape = (height_pixels, width_pixels)

# 2) 개별 속성(rasterize) 예시: FuelLoad
fuel_raster = rasterize(
    [(geom, value) for geom, value in zip(gdf.geometry, gdf["FuelLoad"])],
    out_shape=out_shape,
    transform=transform,
    fill=0,
    dtype="float32"
)
