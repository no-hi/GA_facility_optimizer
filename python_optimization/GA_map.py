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
import matplotlib
matplotlib.rcParams['font.family'] = 'TakaoPGothic' # takao インストール後、matplotlibのフォルダ行ってキャッシュ削除

import data
name = data.name
kanen = data.kanen
sanpai = data.sanpai
def replace_sira(name_list):
    # データがリストの場合、各要素に対して再帰的にこの関数を適用
    if isinstance(name_list, list):
        return [replace_sira(item) for item in name_list]
    # データが文字列の場合、'白糖町'を'白糠町'に置換
    elif isinstance(name_list, str):
        return name_list.replace('白糖町', '白糠町')
    # それ以外のデータ型の場合は、そのまま返す
    else:
        return name_list

##############################################################################



waste_name ='kanen'
unit ='t/year'

inc_size= [444284, 97568, 89908, 80061, 61174, 47662, 42568, 33407, 7726, 7466, 6943, 5075, 4736, 3703, 2604, 1996, 1718, 953, 819, 725]
inc_facility = ['札幌市', '旭川市', '苫小牧市', '函館市', '帯広市', '釧路市', '室蘭市', '北見市', '中標津町', '稚内市', '紋別市', '岩内町', '根室市', 'せたな町', '江差町', '八雲町', '枝幸町', '松前町', '増毛町', '羽幌町']
inc_blocks = [['札幌市', '石狩市'], ['寿都町', '黒松内町', '蘭越町', 'ニセコ町', '真狩村', '留寿都村', '喜茂別町', '京極町', '俱知安町', '共和町', '岩内町', '泊村', '神恵内村', '仁木町', '赤井川村'], ['室蘭市'], ['苫小牧市', '白老町', '厚真町', 'むかわ町', '日高町', '平取町'], ['函館市', '北斗市'], ['八雲町', '長万部町'], ['江差町', '上ノ国町', '厚沢部町', '乙部町'], ['島牧村', '今金町', 'せたな町'], ['深川市', '秩父別町', '沼田町', '旭川市', '鷹栖町', '東神楽町', '当麻町', '比布町', '愛別町', '上川町', '東川町', '美瑛町', '和寒町', '幌加内町'], ['中川町', '苫前町', '羽幌町', '初山別村', '遠別町', '天塩町'], ['松前町', '福島町'], ['留萌市', '増毛町', '小平町'], ['稚内市', '猿払村', '豊富町', '幌延町'], ['音威子府村', '浜頓別町', '中頓別町', '枝幸町'], ['北見市', '美幌町', '津別町', '訓子府町', '置戸町', '佐呂間町', '陸別町'], ['紋別市', '湧別町', '滝上町', '興部町', '西興部村', '雄武町'], ['帯広市', '音更町', '士幌町', '上士幌町', '鹿追町', '新得町', '清水町', '芽室町', '中札内村', '更別村', '幕別町', '池田町', '豊頃町', '本別町', '足寄町', '浦幌町'], ['釧路市', '釧路町', '鶴居村', '白糠町'], ['根室市'], ['斜里町', '別海町', '中標津町', '標津町', '羅臼町']]

trans_size=[33729, 27992, 27117, 18988, 11493, 11426, 10694, 9859, 7532, 7257, 5250, 4896, 3259, 2674, 2406, 2358, 2357, 2144, 1929, 1005]
trans_facility = ['千歳市', '小樽市', '江別市', '岩見沢市', '北広島市', '登別市', '伊達市', '滝川市', '網走市', '七飯町', '新ひだか町', '士別市', '芦別市', '上富良野町', '浦河町', '標茶町', '遠軽町', '大樹町', '厚岸町', '木古内町']
trans_blocks = [['登別市'], ['夕張市', '岩見沢市', '美唄市', '三笠市', '栗山町', '月形町', '新篠津村'], ['滝川市', '砂川市', '奈井江町', '上砂川町', '浦臼町', '新十津川町', '妹背牛町', '雨竜町', '北竜町'], ['南幌町', '江別市', '当別町'], ['千歳市', '恵庭市', '安平町'], ['由仁町', '長沼町', '北広島市'], ['芦別市', '赤平市', '歌志内市'], ['小樽市', '積丹町', '古平町', '余市町'], ['伊達市', '豊浦町', '壮瞥町', '洞爺湖町'], ['浦河町', '様似町', 'えりも町'], ['新冠町', '新ひだか町'], ['標茶町', '弟子屈町'], ['七飯町', '鹿部町', '森町'], ['士別市', '名寄市', '剣淵町', '下川町', '美深町'], ['富良野市', '上富良野町', '中富良野町', '南富良野町', '占冠村'], ['網走市', '清里町', '小清水町', '大空町'], ['遠軽町'], ['知内町', '木古内町'], ['大樹町', '広尾町'], ['厚岸町', '浜中町']]

arrows = [[['札幌市'], ['小樽市', '岩見沢市', '北広島市', '江別市']], [['室蘭市'], ['登別市', '伊達市']], [['苫小牧市'], ['千歳市', '浦河町', '新ひだか町']], [['函館市'], ['木古内町', '七飯町']], [['旭川市'], ['士別市', '上富良野町', '芦別市', '滝川市']], [['北見市'], ['網走市']], [['紋別市'], ['遠軽町']], [['帯広市'], ['大樹町']], [['釧路市'], ['厚岸町', '標茶町']]]

# t/day
if unit == "t/day":
    inc_size = [x / 365 for x in inc_size]
    trans_size = [x / 365 for x in trans_size]


##############################################################################
inc_facility = replace_sira(inc_facility)
inc_blocks = replace_sira(inc_blocks)
trans_facility = replace_sira(trans_facility)
trans_blocks = replace_sira(trans_blocks)
arrows = replace_sira(arrows)


if waste_name == "kanen":
    symbolsize = 0.5
    
if waste_name == "sanpai":
    symbolsize = 0.1

if unit == "t/year":
    symbolsize = symbolsize/365

waste = globals()[waste_name]
block0 = [name[i] for i in range(len(kanen)) if kanen[i] == 0] # ごみなし地域
blocks = [block0] + inc_blocks + trans_blocks
N_block = len(blocks)
facility = inc_facility + trans_facility
size = inc_size + trans_size

# tab20
colors = cm.tab20(np.linspace(0, 1, len(inc_blocks)-1))  # カラーマップから色を取得
# + ["yellow"] 必要分付け足す
block_color = ["white"] + list(colors)+ ["yellow"] + ["red" for _ in trans_blocks]  # 残りのブロックに色を割り当て

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
    if row["市町村"] in trans_facility:
        # trans_facilityに該当する施設のマーカーを黒塗りの三角形に設定
        ax.scatter(representative_point.x, representative_point.y, color="white", s=row["施設規模"]*symbolsize, edgecolor="black", linewidth=1, marker="^")
    else:
        # それ以外の施設は白塗りの円形で表示（以前の設定を維持）
        ax.scatter(representative_point.x, representative_point.y, color="white", s=row["施設規模"]*symbolsize, edgecolor="black", linewidth=1.75, marker="o")


# 矢印を描画
for pair in arrows:
    inc_list, trans_list = pair
    
    for inc in inc_list:
        for trans in trans_list:
            inc_point = gdf[gdf["短縮名称"] == inc]["geometry"].representative_point().iloc[0]
            trans_point = gdf[gdf["短縮名称"] == trans]["geometry"].representative_point().iloc[0]
            # 出発地から目的地へ矢印を描画
            ax.annotate("", xy=(inc_point.x, inc_point.y), xytext=(trans_point.x, trans_point.y),
                        arrowprops=dict(arrowstyle="->", color="blue", linewidth=1.25))


# 凡例用のダミーマーカーを作成
if waste_name == "kanen":
    if unit == "t/year":
        legend_markers = [plt.scatter([], [], s=size*symbolsize, edgecolor="black", linewidth=1.75, color="white", marker="o") for size in [10000, 100000, 0,500000,0]]
    if unit == "t/day":
        legend_markers = [plt.scatter([], [], s=size*symbolsize, edgecolor="black", linewidth=1.75, color="white", marker="o") for size in [10, 100, 1000,0]]

if waste_name == "sanpai":
    if unit == "t/year":
        legend_markers = [plt.scatter([], [], s=size*symbolsize, edgecolor="black", linewidth=1.75, color="white", marker="o") for size in [10000, 100000,1000000]]
    if unit == "t/day":
        legend_markers = [plt.scatter([], [], s=size*symbolsize, edgecolor="black", linewidth=1.75, color="white", marker="o") for size in [10, 100,1000,0]]



# 凡例のラベル
if waste_name == "kanen":
    if unit == "t/year":
        legend_labels = ["1万", "10万","", "50万",""]
    if unit == "t/day":
        legend_labels = ["10", "100", "1000",""]

if waste_name == "sanpai":
    if unit == "t/year":
        legend_labels = ["1万", "10万", "100万"]
    if unit == "t/day":
        legend_labels = ["10", "100", "1000",""]

# 凡例をプロットに追加
plt.legend(legend_markers, legend_labels, scatterpoints=1, frameon=True, labelspacing=1, title= f'施設規模{unit}')

plt.show()
