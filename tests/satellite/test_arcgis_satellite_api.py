import os
import sys 
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
root_dir = os.path.dirname(parentdir)
sys.path.insert(0,root_dir) 

import unittest
from arcgis_satellite_api.satellite import arcgis_satellite_api as sd


sat = sd.Satellite_data()

class TestArcgisAPI(unittest.TestCase):
    def test__init(self):
        assert sat.notfound is not None
        assert sat.notfound_avg is not None
        assert len(sat.notfound_avg) == 3

if __name__ == '__main__':
    unittest.main()