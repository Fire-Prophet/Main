import sys
from qgis.core import QgsApplication, QgsRasterLayer

QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/MacOS", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# DEM 래스터 레이어 불러오기
raster_path = "/path/to/your/dem.tif"  # DEM 파일 경로
layer = QgsRasterLayer(raster_path, "DEM Layer")
if not layer.isValid():
    print("DEM layer failed to load!")
else:
    print("DEM layer loaded successfully!")

qgs.exitQgis()
