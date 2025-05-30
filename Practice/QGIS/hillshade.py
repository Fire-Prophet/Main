import sys
from qgis.core import QgsApplication, QgsRasterLayer, QgsProcessingFeedback
from qgis import processing

QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/MacOS", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# 힐셰이딩(지형 음영) 생성
raster_path = "/path/to/your/dem.tif"
hillshade_path = "/path/to/output/hillshade.tif"
layer = QgsRasterLayer(raster_path, "DEM Layer")
if layer.isValid():
    processing.run("gdal:hillshade", {
        'INPUT': raster_path,
        'BAND': 1,
        'Z_FACTOR': 1.0,
        'AZIMUTH': 315.0,
        'ALTITUDE': 45.0,
        'COMPUTE_EDGES': True,
        'ZEVENBERGEN': False,
        'MULTIDIRECTIONAL': False,
        'OUTPUT': hillshade_path
    }, feedback=QgsProcessingFeedback())
    print("Hillshade raster generated!")
else:
    print("DEM layer failed to load!")

qgs.exitQgis()
