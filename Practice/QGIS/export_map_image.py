import sys
from qgis.core import QgsApplication, QgsRasterLayer, QgsMapRendererParallelJob, QgsMapSettings
from qgis.PyQt.QtGui import QImage
from qgis.PyQt.QtCore import QSize

QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/MacOS", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# 지도 이미지로 내보내기
raster_path = "/path/to/your/dem.tif"
output_image = "/path/to/output/map.png"
layer = QgsRasterLayer(raster_path, "DEM Layer")
if layer.isValid():
    settings = QgsMapSettings()
    settings.setLayers([layer])
    settings.setOutputSize(QSize(800, 600))
    settings.setExtent(layer.extent())
    image = QImage(QSize(800, 600), QImage.Format_ARGB32_Premultiplied)
    image.fill(0)
    job = QgsMapRendererParallelJob(settings)
    job.start()
    job.waitForFinished()
    image = job.renderedImage()
    image.save(output_image, "png")
    print("Map exported as image!")
else:
    print("DEM layer failed to load!")

qgs.exitQgis()
