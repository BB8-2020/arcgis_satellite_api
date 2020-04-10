import inspect
import os
import sys

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from arcgis_satellite_api.satellite import arcgis_satellite_api as sat

sd = sat.Satellite_data()
data = sd.download_tile(52.084323, 5.175941)

print(data)
