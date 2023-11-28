import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Excelファイルの読み込み
file_path = '/mnt/data/clean_facilities_data - コピー.xlsx'
facilities_df = pd.read_excel(file_path)

# シェープファイルの読み込み（北海道の地理的データ）
shapefile_path = '/mnt/data/N03-20230101_01_GML.zip'
hokkaido_map = gpd.read_file(shapefile_path)

# 施設データフレームに地理的ポイントを作成
facilities_df['geometry'] = gpd.points_from_xy(facilities_df['経度'], facilities_df['緯度'])
geo_facilities_df = gpd.GeoDataFrame(facilities_df, geometry='geometry')

# 地理データフレームの座標参照系を設定
geo_facilities_df.set_crs(epsg=4326, inplace=True)

# 座標参照系を北海道の地図に合わせて変換
geo_facilities_df = geo_facilities_df.to_crs(hokkaido_map.crs)

# 北海道の地図に施設の位置をプロット
fig, ax = plt.subplots(figsize=(15, 15))
hokkaido_map.plot(ax=ax, color='white', edgecolor='black')
geo_facilities_df.plot(ax=ax, color='red', markersize=geo_facilities_df['年間処理量（t/年度）'] / 1000, alpha=0.5)

# タイトルとラベルを設定
ax.set_title('Facilities in Hokkaido with Size Representing Annual Processing Volume')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

plt.show()
