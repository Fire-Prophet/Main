import sys
from qgis.core import QgsApplication, QgsRasterLayer, QgsProcessingFeedback
from qgis import processing

QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/MacOS", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# 등고선 생성
raster_path = "/path/to/your/dem.tif"
contour_path = "/path/to/output/contours.shp"
layer = QgsRasterLayer(raster_path, "DEM Layer")
if layer.isValid():
    processing.run("gdal:contour", {
        'INPUT': raster_path,
        'BAND': 1,
        'INTERVAL': 10,  # 등고선 간격(m)
        'FIELD_NAME': 'ELEV',
        'OUTPUT': contour_path
    }, feedback=QgsProcessingFeedback())
    print("Contours generated!")
else:
    print("DEM layer failed to load!")

qgs.exitQgis()
