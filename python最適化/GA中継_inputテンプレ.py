import data
hokkaido = data.name
# TOP_N_CITIES = N_INC + N_TRANS +10          # ごみ量順位下限→ループ内で設定

restarting_output_directory = ""

add_name = ""
waste_name = "kanen"
# waste_name = "sanpai"
N_CITIES = len(hokkaido)   # 市町村数
N_INC_INITIAL = 1          # 焼却初期値
N_INC_MAX = 10             # 焼却上限
N_TRANS_INITIAL = 0        # 中継初期値
N_TRANS_MAX = 10           # 中継上限
N_IND_UNIT = 50            # 1施設当たり個体数
N_GEN = 1000               # 世代数
CX_PROB = 0.7              # 一様交叉
MUT_PROB = 0.3             # 突然変異
TOUR_SIZE = 4              # トーナメント
ELITE_SIZE = 0.1           # エリートサイズ
UNIT_TRANS = 877           # 2tパッカー車輸送単価
UNIT_TRANS2 = 313          # 10t大型車輸送単価
