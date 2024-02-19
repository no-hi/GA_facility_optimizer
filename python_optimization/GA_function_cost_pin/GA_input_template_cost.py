import data as data
hokkaido = data.name
# TOP_N_CITIES = N_INC + N_TRANS +10          # ごみ量順位下限→ループ内で設定

add_name = ""
waste_name = "kanen"
# waste_name = "sanpai"


restarting_output_directory = "877kanen21~22&11~20_20240130_145827"    # 再開したい中断フォルダ名
N_CITIES = len(hokkaido)   # 市町村数
N_INC_INITIAL = 1          # 焼却初期値
N_INC_MAX = 3             # 焼却上限
N_TRANS_INITIAL = 0        # 中継初期値
N_TRANS_MAX = 0           # 中継上限
N_IND_UNIT = 50            # 1施設当たり個体数
N_GEN = 100               # 世代数
CX_PROB = 0.7              # 一様交叉
MUT_PROB = 0.3             # 突然変異
TOUR_SIZE = 4              # トーナメント
ELITE_SIZE = 0.1           # エリートサイズ
UNIT_TRANS = 877           # 2tパッカー車輸送単価
UNIT_TRANS2 = 313          # 10t大型車輸送単価
