import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 形状ファイルを読み込む
gdf = gpd.read_file('./paintpy/hokkaido_map_geosontoshp/hokkaido_map.shp')

# ごみ量データを読み込む
waste_data = pd.read_excel('../nohi3.10/excelpy/waste_data.xlsx', engine='openpyxl')

# ごみ量データを形状データにマージ
gdf = gdf.merge(waste_data, how='left', left_on='市町村名', right_on='name')

# ごみ量のデータを平方根変換
gdf['waste_sqrt'] = np.sqrt(gdf['waste'])

# マップをプロット　#赤　→　YlOrRd
gdf.plot(column='waste_sqrt', cmap='Blues', legend=True)
plt.show()

#等分階級で色分け
#gdf.plot(column='waste_sqrt', cmap='Blues', scheme='quantiles', legend=True)
#plt.show()



