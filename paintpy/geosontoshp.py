import geopandas as gpd

# GeoJSONファイルを読み込み
gdf = gpd.read_file('./hokkaido_map_geosontoshp/hokkaido_map.geojson')

# Shapefileに変換して保存
gdf.to_file('hokkaido_map.shp', driver='ESRI Shapefile', encoding='shift-jis')
gdf['市町村名'] = gdf['市町村名'].str.encode('utf-8').str.decode('ISO-8859-1')
