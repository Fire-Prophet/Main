import sys
from qgis.core import QgsApplication, QgsRasterLayer, QgsProcessingFeedback
from qgis import processing

QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/MacOS", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# 경사도 분석
raster_path = "/path/to/your/dem.tif"
slope_path = "/path/to/output/slope.tif"
layer = QgsRasterLayer(raster_path, "DEM Layer")
if layer.isValid():
    processing.run("gdal:slope", {
        'INPUT': raster_path,
        'BAND': 1,
        'SCALE': 1.0,
        'AS_PERCENT': False,
        'COMPUTE_EDGES': True,
        'ZEVENBERGEN': False,
        'OUTPUT': slope_path
    }, feedback=QgsProcessingFeedback())
    print("Slope raster generated!")
else:
    print("DEM layer failed to load!")

qgs.exitQgis()
