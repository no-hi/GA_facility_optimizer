import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def string(input):
    items = input.split(",")
    output = [f"{item.strip()}" for item in items]
    return output 

select = string("札幌市, 本別町, 函館市")
size=[685009,167311,90136]
N_block=3+1
# #RRGGBB の形式で色を表すコードで、RR、GG、BB は赤、緑、青の成分を表す2桁の16進数です。例えば、赤は #FF0000、緑は #00FF00、青は #0000FF
# RGBまたはRGBAタプル：赤、緑、青の成分（透明度を表すアルファ成分をオプションで）を0から1の範囲で指定するタプルを使用できます。例えば、赤は (1, 0, 0)、緑は (0, 1, 0)、青は (0, 0, 1) です。
# 「yellow」「purple」「orange」「pink」「brown」「black」「white」「gray」
block_color=["white","blue", "green", "red"]
block0 = string("倶知安町, 白糠町")
block1 = string("夕張市, 岩見沢市, 美唄市, 芦別市, 赤平市, 三笠市, 滝川市, 砂川市, 歌志内市, 深川市, 南幌町, 奈井江町, 上砂川町, 由仁町, 長沼町, 栗山町, 月形町, 浦臼町, 新十津川町, 妹背牛町, 秩父別町, 雨竜町, 北竜町, 沼田町, 札幌市, 江別市, 千歳市, 恵庭市, 北広島市, 石狩市, 当別町, 新篠津村, 小樽市, 寿都町, 蘭越町, ニセコ町, 真狩村, 留寿都村, 喜茂別町, 京極町, 俱知安町, 共和町, 岩内町, 泊村, 神恵内村, 積丹町, 古平町, 仁木町, 余市町, 赤井川村, 室蘭市, 苫小牧市, 登別市, 伊達市, 豊浦町, 壮瞥町, 白老町, 厚真町, 洞爺湖町, 安平町, むかわ町, 日高町, 平取町, 新冠町, 新ひだか町, 旭川市, 士別市, 名寄市, 富良野市, 鷹栖町, 東神楽町, 当麻町, 比布町, 東川町, 美瑛町, 上富良野町, 中富良野町, 占冠村, 和寒町, 剣淵町, 美深町, 音威子府村, 中川町, 幌加内町, 留萌市, 増毛町, 小平町, 苫前町, 羽幌町, 初山別村, 遠別町, 天塩町, 稚内市, 中頓別町, 豊富町, 礼文町, 利尻町, 利尻富士町, 幌延町")
block2 = string("浦河町, 様似町, えりも町, 愛別町, 上川町, 南富良野町, 下川町, 猿払村, 浜頓別町, 枝幸町, 北見市, 網走市, 紋別市, 美幌町, 津別町, 清里町, 斜里町, 小清水町, 訓子府町, 置戸町, 佐呂間町, 遠軽町, 湧別町, 滝上町, 興部町, 西興部村, 雄武町, 大空町, 帯広市, 音更町, 士幌町, 上士幌町, 鹿追町, 新得町, 清水町, 芽室町, 中札内村, 更別村, 大樹町, 広尾町, 幕別町, 池田町, 豊頃町, 本別町, 足寄町, 陸別町, 浦幌町, 釧路市, 釧路町, 厚岸町, 浜中町, 標茶町, 弟子屈町, 鶴居村, 白糖町, 根室市, 別海町, 中標津町, 標津町, 羅臼町")
block3 = string("島牧村, 黒松内町, 函館市, 北斗市, 松前町, 福島町, 知内町, 木古内町, 七飯町, 鹿部町, 森町, 八雲町, 長万部町, 江差町, 上ノ国町, 厚沢部町, 乙部町, 奥尻町, 今金町, せたな町")
block = block0,block1,block2,block3

# シェープファイルの読み込み
shp_file_path = "C:\\Users\\hyo15\\remote_nohi_11_16\\hokkaido_shp\\hokkaido_sapporo_diffusion.shp"
gdf = gpd.read_file(shp_file_path, encoding="shift-jis")

# 選択された市町村とその施設サイズのためのDataFrameを作成
selected_data = pd.DataFrame({"市町村": select, "施設規模": size})

# 選択されたデータをGeoDataFrameと結合
selected_municipalities = gdf.merge(selected_data, left_on="短縮名称", right_on="市町村")  # "市町村名"を実際の列名に置き換えてください

# 市町村にブロックを割り当て
for i, block in enumerate(block):
    gdf.loc[gdf["短縮名称"].isin(block), "block"] = i  # ここも"市町村名"を実際の列名に置き換えてください

# 特定の施設サイズとブロックの色分けでプロット
fig, ax = plt.subplots(1, 1, figsize=(15, 15))

# 各ブロックをその色でプロット
for i in range(N_block):
    gdf[gdf["block"] == i].plot(ax=ax, color=block_color[i], edgecolor="black", linestyle="--")

# 施設を選択された市町村に重ねて表示
for _, row in selected_municipalities.iterrows():
    representative_point = row["geometry"].representative_point()
    ax.scatter(representative_point.x, representative_point.y, color="gray", s=row["施設規模"]*0.001, edgecolor="black", marker="o")  # 施設サイズのスケールを調整

ax.set_title("廃棄物施設配置マップ（北海道）")
plt.show()
