import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

def generate_contours(data):
    points = np.array([[d['lon'], d['lat']] for d in data])
    values = [d['risk'] for d in data]

    xi = np.linspace(min(points[:,0]), max(points[:,0]), 100)
    yi = np.linspace(min(points[:,1]), max(points[:,1]), 100)
    zi = griddata(points, values, (xi[None, :], yi[:, None]), method='cubic')

    # 등고선 시각화 및 GeoJSON 변환 (생략)
