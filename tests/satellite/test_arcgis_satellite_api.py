import os

from arcgis_satellite_api.satellite.arcgis_satellite_api import Satellite_data

ARCGIS = Satellite_data()


def test_convert_base64_to_np_array():
    """Tests the base64 image to np array function.

    Tests the buffer_to_bgr function which is supposed to convert
    a base64 string to a numpy BGR array. A BGR array is basically
    an array of Blue, Red, Green values. We also need to make sure
    this array has a module type of numpy.

    """
    cwd = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(cwd, 'test_image_base64.txt')) as text_file:
        base64_img = text_file.read()

    res = ARCGIS.convert_base64_to_np_array(base64_img)
    assert type(res).__module__ == 'numpy'


def test_download_tile():
    """ Tests the download_tile function.

    Tests the download_tile function which is supposed to return
    a base64 string when the as_base64 argument is set to true.
    We don't actually test the values of this function because it
    scales down dynamically based on the availability of the tile
    on this zoom level. It's dependent on the get_zoom_level_image
    function which has this inherent property.

    """
    res = ARCGIS.download_tile(1, 1, as_base64=True)

    assert 'bounds' in res
    assert 'coordinate_pixel' in res
    assert 'zoom' in res
    assert 'base64' in res


def test_get_zoom_level_image():
    """ Tests the get_zoom_level_image function.

    This function tests the expected values and return types
    of the get_zoom_level_image function. We don't actually
    test the values of this function because it scales down
    dynamically if it can't find an image at this zoom level.

    """
    res = ARCGIS.get_zoom_level_image(1, 1, 17)
    assert type(res) == tuple
    assert len(res) == 4

    assert type(res[0]) == str  # Image as base64
    assert type(res[1]) == int  # Tile x value
    assert type(res[2]) == int  # Tile y value
    assert type(res[3]) == int  # Zoom level


def test_long_to_tile_X():
    """ This function tests the long_to_tile_X function.

    We test this function on a constant input and make sure
    that our calculation matches the expected result.

    """
    res = ARCGIS.long_to_tile_X(1, 17)
    assert type(res) == int
    assert res == 65900


def test_lat_to_tile_Y():
    """ This function tests the lat_to_tile_Y function.

    We test this function on a constant input and make sure
    that our calculation matches the expected result.

    """
    res = ARCGIS.lat_to_tile_Y(1, 17)
    assert type(res) == int
    assert res == 65171


def test_get_top_left_bound():
    """ This function tests the get_top_left_bound function.

    It gets tested on it's types and on the expected values.

    """
    res = ARCGIS.get_top_left_bound(1, 1, 17)
    assert len(res) == 2
    assert type(res) == tuple
    assert type(res[0]) == float
    assert type(res[1]) == float
    assert res[0] == 85.05089183547521
    assert res[1] == -179.99725341796875


def test_get_bounds():
    """ This function tests the get_bounds function.

    It gets tested on it's types and on the expected values.

    """
    res = ARCGIS.get_bounds(1, 1, 17)
    assert len(res) == 2
    assert type(res) == tuple
    # Top left
    assert type(res[0]) == tuple
    assert type(res[0][0]) == float
    assert type(res[0][1]) == float
    assert res[0][0] == 85.05089183547521
    assert res[0][1] == -179.99725341796875
    # Bottom right
    assert type(res[1]) == tuple
    assert type(res[1][0]) == float
    assert type(res[1][1]) == float
    assert res[1][0] == 85.05065487982755
    assert res[1][1] == -179.9945068359375


def test_get_lat_lng_from_pixel():
    """ This function tests the get_lat_lng_from_pixel function.

    It gets tested on it's types and on the expected values.

    """
    res = ARCGIS.get_lat_lng_from_pixel(
        loc={ "x": 1, "y": 1 },
        bound_top_left={
            'lat': 0,
            'lon': 0
        },
        bound_bottom_right={
            'lat': 1,
            'lon': 1
        }
    )

    assert type(res) == dict

    assert 'lat' in res
    assert type(res['lat']) == float
    assert res['lat'] == 0.99609375

    assert 'lon' in res
    assert type(res['lon']) == float
    assert res['lon'] == 0.00390625


def test_get_box_lat_lng():
    """ This function tests the get_box_lat_lng function. """
    res = ARCGIS.get_box_lat_lng(
        box={ "x1": 1, "y1": 1, "x2": 2, "y2": 2 },
        bound_top_left={
            'lat': 0,
            'lon': 0
        },
        bound_bottom_right={
            'lat': 1,
            'lon': 1
        }
    )

    assert type(res) == dict

    assert 'top_left' in res
    assert type(res['top_left']) == dict
    assert 'lat' in res['top_left']
    assert 'lon' in res['top_left']
    assert type(res['top_left']['lat']) == float
    assert type(res['top_left']['lon']) == float
    assert res['top_left']['lat'] == 0.99609375
    assert res['top_left']['lon'] == 0.00390625

    assert 'bottom_right' in res
    assert type(res['bottom_right']) == dict
    assert 'lat' in res['bottom_right']
    assert 'lon' in res['bottom_right']
    assert type(res['bottom_right']['lat']) == float
    assert type(res['bottom_right']['lon']) == float
    assert res['bottom_right']['lat'] == 0.9921875
    assert res['bottom_right']['lon'] == 0.0078125


def test_get_pixel_location():
    """ This function tests the get_pixel_location function. """
    res = ARCGIS.get_pixel_location(
        loc=(1, 1),
        bound_top_left=(0, 0),
        bound_bottom_right=(1, 1)
    )

    assert type(res) == tuple
    assert type(res[0]) == int
    assert type(res[1]) == int
    assert res[0] == 256
    assert res[1] == 256
