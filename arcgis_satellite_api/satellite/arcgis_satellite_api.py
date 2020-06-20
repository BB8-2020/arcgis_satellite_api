import base64
import math
import os
from io import BytesIO

from PIL import Image
import numpy as np
import requests


class Satellite_data():
    """ Class to reach the Arcgis World Imagery Web API. """

    def __init__(self):
        """ Constructor method, registers the not found image. """
        self.base_url = "https://server.arcgisonline.com/arcgis/rest/services"
        self.tile_maps = {
            'world_imagery': 'World_Imagery',
            'world_hillshade': 'Elevation/World_Hillshade',
            'world_hillshade_dark': 'Elevation/World_Hillshade_Dark'
        }

        cwd = os.path.dirname(os.path.abspath(__file__))
        self.data_folder = os.path.join(cwd, 'data')
        with open(os.path.join(self.data_folder, 'not_found_base64.txt')) as not_found_img:
            self.not_found_img = not_found_img.read()

    def convert_base64_to_np_array(self, base64_img):
        """ Converts a base64 string to a np array.

        An image is provided in base64 form, this is decoded into a decoded string.
        This value is then passed into a BytesIO which transforms it into a bytes object.
        The bytes object is then finally read by PIL and converted to an RGB numpy array.
        Lastly the numpy array is transformed from RGB to BGR since our model expects these inputs.

        :param base64_img: An image in base64 string form.
        :type base64_img: string
        :return: A numpy BGR image array
        :rtype: np.array
        """
        msg = base64.b64decode(base64_img)
        buf = BytesIO(msg)
        image = np.asarray(Image.open(buf).convert('RGB'))
        image[:, :, ::-1].copy()
        return image

    def download_tile(self, lat, lon, zoom=23, map_type="world_imagery", as_base64=False):
        """ Download a tile from the Arcgis World Imagery API.

        :param lat: Latitude value from desired tile.
        :type lat: float
        :param lon: Longitude value from desired tile.
        :type lon: float
        :param zoom: Zoom level of desired tile.
        :type zoom: int
        :param map_type: Desired map type, currently supports:
            world_imagery,
            world_hillshade,
            world_hillshade_dark. (http://server.arcgisonline.com/arcgis/rest/services/)
        :type map_type: str
        :param zoom: Whether to return a base64 sring or save as local image.
        :type zoom: boolean
        :return: Dictionary with filename of downloaded image,
            top left & right bottom bound in (lat,lon) values, pixel where given coordinate is located (x,y) and zoom level.
        :rtype: dict
        """

        image, tile_x, tile_y, zoom = self.get_zoom_level_image(
            lat,
            lon,
            zoom=zoom,
            map_type=map_type
        )

        bound_top_left, bound_bottom_right = self.get_bounds(
            tile_x,
            tile_y,
            zoom
        )

        coordinate_pixel_x, coordinate_pixel_y = self.get_pixel_location(
            loc=(lat, lon,),
            bound_top_left=bound_top_left,
            bound_bottom_right=bound_bottom_right
        )

        tile_data = {
            'bounds': {
                'top_left': bound_top_left,
                'bottom_right': bound_bottom_right,
            },
            'coordinate_pixel': {
                'x': coordinate_pixel_x,
                'y': coordinate_pixel_y
            },
            'zoom': zoom
        }

        if not as_base64:
            if not os.path.isdir(f"{self.data_folder}images"):
                os.mkdir(f"{self.data_folder}images")

            filename = f"{self.data_folder}images/{map_type}_{tile_x}_{tile_y}_{zoom}.jpeg"
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(image))

            tile_data['filename'] = filename
        else:
            tile_data['base64'] = image

        return tile_data

    def get_zoom_level_image(self, lat, lon, zoom, map_type="world_imagery"):
        """ Get a tile from the Arcgis World Imagery API with desired zoomlevel.

        :param lat: Latitude value from desired tile.
        :type lat: float
        :param lon: Longitude value from desired tile.
        :type lon: float
        :param zoom: Zoom level of desired tile.
        :type zoom: int
        :param map_type: Desired map type, currently supports:
            world_imagery,
            world_hillshade,
            world_hillshade_dark. (http://server.arcgisonline.com/arcgis/rest/services/)
        :type map_type: str
        :return: Desired image as base64, tile x-value, tile y-value,
            zoomlevel of retrieved image.
        :rtype: str, int, int, int

        .. note::
            When an image on the desired zoom level is not available,
                there will be searched for a lower resolution image. Desired zoomlevel is not guaranteed.
        """

        if zoom < 0 or zoom > 23:
            raise Exception("Zoom can't be lower than 0 or higher than 23.")

        tile_y = self.lat_to_tile_Y(lat, zoom)
        tile_x = self.long_to_tile_X(lon, zoom)

        image_url = f"{self.base_url}/{self.tile_maps[map_type]}/MapServer/tile/{zoom}/{tile_y}/{tile_x}"

        response = requests.get(image_url)
        image = str(base64.b64encode(response.content), 'utf-8')

        if image == self.not_found_img:
            return self.get_zoom_level_image(lat, lon, zoom - 1, map_type)

        return (image, tile_x, tile_y, zoom)

    def long_to_tile_X(self, lon, zoom):
        """Calculate tile x-value based on longitude and zoom value.

        :param lon: Longitude value.
        :type lon: float
        :param zoom: Zoom level.
        :type zoom: int
        :return: Tile x-value
        :rtype: int
        """
        return math.floor((lon + 180) / 360 * math.pow(2, zoom))

    def lat_to_tile_Y(self, lat, zoom):
        """Calculate tile y-value based on latitude and zoom value.

        :param lat: Latitude value.
        :type lat: float
        :param zoom: Zoom level.
        :type zoom: int
        :return: Tile y-value
        :rtype: int
        """

        return math.floor(
            (1 - math.log(
                math.tan(lat * math.pi / 180) + 1 / math.cos(lat * math.pi / 180)
            ) / math.pi) / 2 * math.pow(2, zoom)
        )

    def get_top_left_bound(self, tile_x, tile_y, zoom):
        """ Get top left bound of an image.

        :param tile_x: Tile x value. Can be calculated with `long_to_tile_X`.
        :type tile_x: int
        :param tile_y: Tile y value. Can be calculated with `lat_to_tile_Y`.
        :type tile_y: int
        :param zoom: Zoom level of image.
        :type zoom: int
        :return: Top left bound (lat, lon) values
        :rtype: (float, float)
        """
        n = 2.0 ** zoom
        lon_deg = tile_x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)

    def get_bounds(self, tile_x, tile_y, zoom):
        """Get bounds of image with defined tile x-value and y-value.

        :param tile_x: Tile x value. Can be calculated with `long_to_tile_X`.
        :type tile_x: int
        :param tile_y: Tile y value. Can be calculated with `lat_to_tile_Y`.
        :type tile_y: int
        :param zoom: Zoom level of image.
        :type zoom: int
        :return: Top left bound (lat, lon) values, bottom right (lat, lon) values.
        :rtype: ((float, float), (float, float))
        """
        top_left = self.get_top_left_bound(tile_x, tile_y, zoom)
        bottom_right = self.get_top_left_bound(tile_x + 1, tile_y + 1, zoom)
        return (top_left, bottom_right)

    def get_lat_lng_from_pixel(self, loc, bound_top_left, bound_bottom_right, img_size=256):
        """ Converts a pixel value to a lat/lng.

        This function turns a pixel value into a latitude or longitude
        based on the top left bound and bottom right bound of the tile.

        :param loc: The pixel's location in the tile.
        :type loc: dict
        :param bound_top_left: The top left bound of the tile.
        :type bound_top_left: dict
        :param bound_bottom_right: The bottom right bound of the tile.
        :type bound_bottom_right: dict
        :param img_size: The size of the tile.
        :type img_size: int
        :return: The lat long coordinates of this pixel.
        :rtype: dict
        """
        x_left = bound_top_left['lon']
        y_top = bound_top_left['lat']
        x_right = bound_bottom_right['lon']
        y_bottom = bound_bottom_right['lat']

        x_range = abs(x_right - x_left)
        y_range = abs(y_top - y_bottom)

        x = loc['x']
        y = loc['y']

        lon = x_left + ((x / img_size) * x_range)
        lat = y_bottom - ((y / img_size) * y_range)

        return {
            'lat': lat,
            'lon': lon,
        }

    def get_box_lat_lng(self, box, bound_top_left, bound_bottom_right):
        """ Retrieve a box's lat long coordinates.

        This function turns 4 pixel points inside a tile into
        a lat long representation of a square.

        :param box: The box's pixel values
        :type box: dict
        :param bound_top_left: The top left bound of the tile.
        :type bound_top_left: dict
        :param bound_bottom_right: The bottom right bound of the tile.
        :type bound_bottom_right: dict
        :return: A box in lat long representation.
        :rtype: dict
        """
        top_left = self.get_lat_lng_from_pixel(
            { 'x': box['x1'], 'y': box['y1'] },
            bound_top_left,
            bound_bottom_right,
        )
        bottom_right = self.get_lat_lng_from_pixel(
            { 'x': box['x2'], 'y': box['y2'] },
            bound_top_left,
            bound_bottom_right,
        )

        return {
            'top_left': {
                'lat': top_left['lat'],
                'lon': top_left['lon'],
            },
            'bottom_right': {
                'lat': bottom_right['lat'],
                'lon': bottom_right['lon'],
            }
        }

    def get_pixel_location(self, loc, bound_top_left, bound_bottom_right, img_size=256):
        """ Get pixel location of given  (lat,lon) location in given bounds.

        :param loc: Latitude and Longitude to get pixel location for.
        :type loc: tuple
        :param bound_top_left: Top left bound, latitude and longitude
        :type bound_top_left: tuple
        :param bound_bottom_right: Right bottom bound, latitude and longitude
        :type bound_bottom_right: tuple
        :param img_size: image resolution in pixels, defaults to 256
        :type img_size: int, optional
        :return: Location in pixels of given coordinate
        :rtype: int, int
        """
        x_top, y_left = bound_top_left
        x_bottom, y_right = bound_bottom_right

        x_range = abs(x_bottom - x_top)
        y_range = abs(y_right - y_left)

        lat, lon = loc

        dist_x_top = abs(x_top - lat)
        pixel_x = math.floor((dist_x_top / x_range) * img_size)

        dist_y_left = abs(y_left - lon)
        pixel_y = math.floor((dist_y_left / y_range) * img_size)

        return pixel_x, pixel_y
