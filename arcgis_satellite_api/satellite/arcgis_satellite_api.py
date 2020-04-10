import math
import os
from urllib.request import urlopen

from matplotlib.pyplot import imread, imsave


class Satellite_data():
    """ Class to reach the Arcgis World Imagery Web API."""

    def __init__(self):
        """ Constructor method, registers the not found image + average
        """
        self.data_folder = '/'.join(__file__.replace('\\',
                                                     '/').split('/')[:-1]) + "/data/"
        self.notfound = imread(self.data_folder + "not_found.jpeg")
        self.notfound_avg = self.notfound.mean(axis=0).mean(axis=0)[0:3]

    def download_tile(self, lat, lon, zoom=23):
        """ Download a tile from the Arcgis World Imagery API.

        :param lat: Latitude value from desired tile.
        :type lat: float
        :param lon: Longitude value from desired tile.
        :type lon: float
        :return: Dictionary with filename of downloaded image, top left & right bottom bound in (lat,lon) values and zoom level.
        :rtype: dict
        """

        if not os.path.isdir(f"{self.data_folder}images"):
            os.mkdir(f"{self.data_folder}images")

        image, tile_x, tile_y, zoom = self.get_zoom_level_image(
            lat, lon, zoom=23)

        filename = f"{self.data_folder}images/{tile_x}_{tile_y}_{zoom}.jpeg"
        local_file = open(filename, 'wb')
        imsave(local_file, image)

        bound_top_left, bound_bottom_right = self.get_bounds(
            tile_x, tile_y, zoom)
        coordinate_pixel_x, coordinate_pixel_y = self.get_pixel_val((lat, lon,),
                                                                    bound_top_left, bound_bottom_right)

        return {
            'filename': filename,
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

    def get_zoom_level_image(self, lat, lon, zoom):
        """ Get a tile from the Arcgis World Imagery API with desired zoomlevel.

        :param lat: Latitude value from desired tile.
        :type lat: float
        :param lon: Longitude value from desired tile.
        :type lon: float
        :return: Desired image as Numpy Array, tile x-value, tile y-value, zoomlevel of retrieved image.
        :rtype: numpy.ndarray, tuple, tuple, int

        .. note::
            When an image on the desired zoom level is not available, there will be searched for a lower resolution image. Desired zoomlevel is not guaranteed.

        """

        if zoom < 0 or zoom > 23:
            raise Exception("Zoom can't be lower than 0 or higher than 23.")

        tile_y = self.lat_to_tile_Y(lat, zoom)
        tile_x = self.long_to_tile_X(lon, zoom)

        image_url = f"https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{zoom}/{tile_y}/{tile_x}"
        with urlopen(image_url) as image_file:
            image = imread(image_file, "jpeg")

            img_average = image.mean(axis=0).mean(axis=0)[0:3]
            if all(img_average == self.notfound_avg):
                return self.get_zoom_level_image(lat, lon, zoom - 1)

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
        return (math.floor((1 - math.log(math.tan(lat * math.pi / 180) + 1 / math.cos(lat * math.pi / 180)) / math.pi) / 2 * math.pow(2, zoom)))

    def get_top_left_bound(self, tile_x, tile_y, zoom):
        """ Get top left boud of image.

        :param tile_x: Tile x value. Can be calculated with `long_to_tile_X`.
        :type tile_x: int
        :param tile_y: Tile y value. Can be calculated with `lat_to_tile_Y`.
        :type tile_y: int
        :param zoom: Zoom level of image.
        :type zoom: int
        :return: Top left bound (lat, lon) values
        :rtype: float
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
        :rtype: float, float
        """
        top_left = self.get_top_left_bound(tile_x, tile_y, zoom)
        bottom_right = self.get_top_left_bound(tile_x + 1, tile_y + 1, zoom)
        return (top_left, bottom_right)

    def get_pixel_val(self, loc, bound_top_left, bound_bottom_right, img_size=256):
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


if __name__ == "__main__":
    sat = Satellite_data()
    data = sat.download_tile(52.200523, 5.413112)
    print(data)
