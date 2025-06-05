import sys
from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsVectorLayer
)

# QGIS 어플리케이션 초기화
QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/MacOS", True)  # QGIS 설치 경로에 맞게 수정
qgs = QgsApplication([], False)
qgs.initQgis()

# 벡터 레이어 불러오기 예시
layer = QgsVectorLayer("/path/to/your/shapefile.shp", "Layer Name", "ogr")
if not layer.isValid():
    print("Layer failed to load!")
else:
    print("Layer loaded successfully!")

# QGIS 종료
qgs.exitQgis()