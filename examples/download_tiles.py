from arcgis_satellite_api.satellite import arcgis_satellite_api as sat


sd = sat.Satellite_data()
data1 = sd.download_tile(-0.608854, 34.205806, zoom=13)
data2 = sd.download_tile(-0.608854, 34.205806, map_type="world_hillshade")
data3 = sd.download_tile(-0.608854, 34.205806, map_type="world_hillshade_dark")

print(data1)
print(data2)
print(data3)
