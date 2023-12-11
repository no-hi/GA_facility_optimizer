import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.cm as cm

def string(input):
    items = input.split(",")
    output = [f"{item.strip()}" for item in items]
    return output 

fazility = string("札幌市, 本別町, 函館市")
size=[685009,167311,90136]

block0 = string("倶知安町, 白糠町") #ごみなし地域
blocks = [[],[],[]]
N_block = len(blocks) + 1

colors = cm.tab20c(np.linspace(0, 1, N_block - 1))  # カラーマップから色を取得
block_color = ["white"] + list(colors[1:])  # 残りのブロックに色を割り当て

# シェープファイルの読み込み
shp_file_path = "C:\\Users\\hyo15\\remote_nohi_11_16\\hokkaido_shp\\hokkaido_sapporo_diffusion.shp"
gdf = gpd.read_file(shp_file_path, encoding="shift-jis")

# 選択された市町村とその施設サイズのためのDataFrameを作成
fazility_data = pd.DataFrame({"市町村": fazility, "施設規模": size})

# 選択されたデータをGeoDataFrameと結合
fazility_municipalities = gdf.merge(fazility_data, left_on="短縮名称", right_on="市町村")  # "市町村名"を実際の列名に置き換えてください

# 市町村にブロックを割り当て
for i, block in enumerate(blocks):
    gdf.loc[gdf["短縮名称"].isin(block), "block"] = i

# 特定の施設サイズとブロックの色分けでプロット
fig, ax = plt.subplots(1, 1, figsize=(15, 15))

# 各ブロックをその色でプロット
for i in range(N_block):
    gdf[gdf["block"] == i].plot(ax=ax, color=block_color[i], edgecolor="black", linestyle="--")

# 施設を選択された市町村に重ねて表示
for _, row in fazility_municipalities.iterrows():
    representative_point = row["geometry"].representative_point()
    ax.scatter(representative_point.x, representative_point.y, color="gray", s=row["施設規模"]*0.001, edgecolor="black", marker="o")  # 施設サイズのスケールを調整

ax.set_title("廃棄物施設配置マップ（北海道）")
plt.show()
