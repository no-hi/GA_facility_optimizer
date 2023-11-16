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

# すべての値に小さな定数を加える
min_nonzero = np.min(gdf.loc[gdf['waste'] > 0, 'waste'])
gdf['waste_shifted'] = gdf['waste'] + min_nonzero / 10.0

# データのスケーリングに対数変換を適用
gdf['log_waste_shifted'] = np.log(gdf['waste_shifted'])

# マップをプロット
gdf.plot(column='waste_shifted', cmap='Blues', legend=True)
plt.show()

#等分階級で色分け
#gdf.plot(column='waste_sqrt', cmap='Blues', scheme='quantiles', legend=True)
#plt.show()