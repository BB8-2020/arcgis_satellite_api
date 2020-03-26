import math
import os
from urllib.request import urlopen
from matplotlib.pyplot import imread, imsave


class Satellite_data():
    def __init__(self):
        self.notfound = imread("data/not_found.jpeg")
        self.notfound_avg = self.notfound.mean(axis=0).mean(axis=0)[0:3]
    def download_tile(self, lat, lon):    
        if not os.path.isdir("data/images"):
            os.mkdir('data/images')

        image, tile_x, tile_y, zoom = self.get_zoom_level_image(lat, lon, 23)

        filename = f'data/images/{tile_x}_{tile_y}_{zoom}.jpeg'
        local_file = open(filename, 'wb')
        imsave(local_file, image)

        bounds = self.get_bounds(tile_x, tile_y, zoom)
        return {
            'filename': filename,
            'bounds': {
                'top_left': bounds[0],
                'bottom_right': bounds[1]
            },
            'zoom': zoom
        }
    	
    def get_zoom_level_image(self, lat, lon, zoom):
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
        return math.floor((lon+180) / 360*math.pow(2, zoom))

    def lat_to_tile_Y(self, lat, zoom):
        return (math.floor((1-math.log(math.tan(lat*math.pi/180) + 1/math.cos(lat*math.pi/180))/math.pi)/2 * math.pow(2, zoom)))

    def num2deg(self, tile_x, tile_y, zoom):
        n = 2.0 ** zoom
        lon_deg = tile_x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)

    def get_bounds(self, tile_x, tile_y, zoom):
        top_left = self.num2deg(tile_x, tile_y, zoom)
        right_bottom = self.num2deg(tile_x + 1, tile_y + 1, zoom)
        return (top_left, right_bottom)


if __name__ == "__main__":
    sd = Satellite_data()
    returnval = sd.download_tile(30, 23)
    print(returnval)
