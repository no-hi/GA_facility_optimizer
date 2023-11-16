import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# 形状ファイルを読み込む
gdf = gpd.read_file('./paintpy/hokkaido_map_geosontoshp/hokkaido_map.shp')
#print(gdf.head())
#print(gdf.info())
#print(gdf.describe())

# ごみ量データを読み込む（ここではpandasのDataFrameと仮定）
waste_data = pd.read_excel('../nohi3.10/excelpy/waste_data.xlsx', engine='openpyxl')
#print(waste_data.head())
#print(waste_data.info())

# ごみ量データを形状データにマージ
gdf = gdf.merge(waste_data, how='left', left_on='市町村名', right_on='name')

# マップをプロット
gdf.plot(column='waste', cmap='YlOrRd', legend=True)
plt.show()

#等分階級で色分け
#gdf.plot(column='waste', cmap='Blues', scheme='quantiles', legend=True)
#plt.show()
