import warnings
from shapely.geometry import LineString
from shapely.errors import ShapelyDeprecationWarning
from shapely.geometry import LineString, MultiLineString
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.cm as cm

##############################################################################
waste = "sanpai"

inc_size= [5587, 3668, 2068, 1857, 1179, 977, 892, 668, 579, 468, 459, 313, 302, 271, 267, 262, 235, 229, 225, 180, 170, 126, 119, 113, 99, 96, 80, 67]
inc_facility = ['苫小牧市', '釧路市', '札幌市', '室蘭市', '登別市', '伊達市', '帯広市', '函館市', '旭川市', '江別市', '千歳市', '北見市', '小樽市', '白老町', 'むかわ町', '洞爺湖町', '新十津川町', '標茶町', '厚岸町', '稚内市', '中標津町', '名寄市', '網走市', '俱知安町', '新ひだか町', '紋別市', '今金町', '根室市']
inc_blocks = [['美唄市', '芦別市', '赤平市', '滝川市', '砂川市', '歌志内市', '奈井江町', '上砂川町', '月形町', '浦臼町', '新十津川町', '妹背牛町', '秩父別町', '雨竜町', '北竜町', '沼田町', '留萌市', '増毛町', '小平町', '苫前町', '羽幌町'], ['札幌市', '石狩市'], ['夕張市', '岩見沢市', '三笠市', '南幌町', '由仁町', '長沼町', '栗山町', '江別市', '北広島市', '当別町', '新篠津村'], ['千歳市', '恵庭市', '安平町', '占冠村'], ['小樽市', '積丹町', '古平町', '仁木町', '余市町', '赤井川村'], ['蘭越町', 'ニセコ町', '真狩村', '留寿都村', '喜茂別町', '京極町', '俱知安町', '共和町', '岩内町', '泊村', '神恵内村'], ['室蘭市'], ['苫小牧市'], ['登別市'], ['伊達市', '壮瞥町'], ['白老町'], ['寿都町', '黒松内町', '豊浦町', '洞爺湖町'], ['厚真町', 'むかわ町', '日高町', '平取町'], ['新冠町', '浦河町', '様似町', 'えりも町', '新ひだか町'], ['函館市', '北斗市', '松前町', '福島町', '知内町', '木古内町', '七飯町', '鹿部町', '森町', '江差町', '上ノ国町', '厚沢部町', '乙部町'], ['島牧村', '八雲町', '長万部町', '今金町', 'せたな町'], ['深川市', '旭川市', '富良野市', '鷹栖町', '東神楽町', '当麻町', '比布町', '愛別町', '上川町', '東川町', '美瑛町', '上富良野町', '中富良野町', '和寒町', '幌加内町'], ['士別市', '名寄市', '剣淵町', '下川町', '美深町', '音威子府村', '中川町', '中頓別町', '枝幸町', '西興部村'], ['初山別村', '遠別町', '天塩町', '稚内市', '猿払村', '浜頓別町', '豊富町', '幌延町'], ['北見市', '美幌町', '津別町', '訓子府町', '置戸町', '佐呂間町', '陸別町'], ['網走市', '清里町', '斜里町', '小清水町', '大空町'], ['紋別市', '遠軽町', '湧別町', '滝上町', '興部町', '雄武町'], ['南富良野町', '帯広市', '音更町', '士幌町', '上士幌町', '鹿追町', '新得町', '清水町', '芽室町', '中札内村', '更別村', '大樹町', '広尾町', '幕別町', '池田町', '豊頃町', '本別町', '足寄町', '浦幌町'], ['釧路市', '釧路町', '鶴居村', '白糖町'], ['厚岸町', '浜中町'], ['標茶町', '弟子屈町'], ['根室市'], ['別海町', '中標津町', '標津町', '羅臼町']]

trans_size = []
trans_facility = []
trans_blocks = []

arrows = []

##############################################################################
if waste == "kanen":
    symbolsize = 1
    
if waste == "sanpai":
    symbolsize = 0.02

block0 = ['倶知安町', '白糠町']  # ごみなし地域
blocks = [block0] + inc_blocks + trans_blocks
N_block = len(blocks)
facility = inc_facility + trans_facility
size = inc_size + trans_size

colors = cm.tab20(np.linspace(0, 1, len(inc_blocks)))  # カラーマップから色を取得
block_color = ["white"] + list(colors) + ["red" for _ in trans_blocks]  # 残りのブロックに色を割り当て

# シェープファイルの読み込み
shp_file_path = "C:\\Users\\hyo15\\remote_nohi_11_16\\hokkaido_shp\\hokkaido_sapporo_diffusion.shp"
gdf = gpd.read_file(shp_file_path, encoding="shift-jis")

# 選択された市町村とその施設サイズのためのDataFrameを作成
fazility_data = pd.DataFrame({"市町村": facility, "施設規模": size})

# 選択されたデータをGeoDataFrameと結合
fazility_municipalities = gdf.merge(fazility_data, left_on="短縮名称", right_on="市町村")  # "市町村名"を実際の列名に置き換えてください

# 市町村にブロックを割り当て
block_index = 1
for block in inc_blocks:
    gdf.loc[gdf["短縮名称"].isin(block), "block"] = block_index
    block_index += 1
for block in trans_blocks:
    gdf.loc[gdf["短縮名称"].isin(block), "block"] = block_index
    block_index += 1
gdf.loc[gdf["短縮名称"].isin(block0), "block"] = 0

# 特定の施設サイズとブロックの色分けでプロット
fig, ax = plt.subplots(1, 1, figsize=(6, 6))

# 各ブロックをその色でプロット
for i in range(N_block):
    gdf[gdf["block"] == i].plot(ax=ax, color=block_color[i], edgecolor="black", linestyle="--")

# trans_blocksの各ブロックの外枠を実線で描画
for block in trans_blocks:
    # 合併したジオメトリの外枠を取得
    boundary = gdf[gdf["短縮名称"].isin(block)].unary_union.boundary

    # boundaryがLineStringの場合
    if isinstance(boundary, LineString):
        ax.plot(*boundary.xy, color="black")

    # boundaryがMultiLineStringの場合
    elif isinstance(boundary, MultiLineString):
        for line in boundary.geoms:  # MultiLineStringを個別のLineStringに分割
            ax.plot(*line.xy, color="black")


# 施設を選択された市町村に重ねて表示
for _, row in fazility_municipalities.iterrows():
    representative_point = row["geometry"].representative_point()
    ax.scatter(representative_point.x, representative_point.y, color="gray", s=row["施設規模"]*symbolsize, edgecolor="black", marker="o")  # 施設サイズのスケールを調整

# # 施設を選択された市町村に重ねて表示　(　規模数表示　)
# for _, row in fazility_municipalities.iterrows():
#     representative_point = row["geometry"].representative_point()
#     ax.scatter(representative_point.x, representative_point.y, color="gray", s=row["施設規模"]*1, edgecolor="black", marker="o")
#     ax.text(representative_point.x, representative_point.y, str(row["施設規模"]),
#             fontsize=8, color='black', ha='center', va='center', fontweight='bold',
#             bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))  # テキストの背景色を追加

# 矢印を描画
for pair in arrows:
    inc_list, trans_list = pair
    
    for inc in inc_list:
        for trans in trans_list:
            inc_point = gdf[gdf["短縮名称"] == inc]["geometry"].representative_point().iloc[0]
            trans_point = gdf[gdf["短縮名称"] == trans]["geometry"].representative_point().iloc[0]
            # 出発地から目的地へ矢印を描画
            ax.annotate("", xy=(inc_point.x, inc_point.y), xytext=(trans_point.x, trans_point.y),
                        arrowprops=dict(arrowstyle="->", color="blue"))




plt.show()
