from arcgis_satellite_api.satellite import arcgis_satellite_api as sat
import unittest


class TestArcgisAPI(unittest.TestCase):
    def test__google(self):
        assert sat.image is not None
