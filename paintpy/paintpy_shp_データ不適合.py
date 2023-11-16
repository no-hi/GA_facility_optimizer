import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# 形状ファイルを読み込む
gdf = gpd.read_file('./paintpy/hokkaido_shp/N03-23_01_230101.shp')
#print(gdf.head())
#print(gdf.info())
#print(gdf.describe())

# ごみ量データを読み込む（ここではpandasのDataFrameと仮定）
waste_data = pd.read_excel('waste_data.xlsx', engine='openpyxl')
#print(waste_data.head())
#print(waste_data.info())

# ごみ量データを形状データにマージ

#######
#shp → 市町村名として、札幌市中央区とか他の書き方で入っているので、瞬と作ったやつならいけるかも
#######

gdf = gdf.merge(waste_data, how='left', left_on='N03_004', right_on='name')

# マップをプロット
gdf.plot(column='waste', cmap='YlOrRd', legend=True)
plt.show()
