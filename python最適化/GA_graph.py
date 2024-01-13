import os
import matplotlib.pyplot as plt
import numpy as np

import matplotlib
matplotlib.rcParams['font.family'] = 'TakaoPGothic' # takao インストール後、matplotlibのフォルダ行ってキャッシュ削除
import datetime
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

##############################################################################

#inc(12~14)+trans(0~8)コスト行列
foldername = 'sanpai877'
cost = [[[6299198.7132645985, 0, 2802968.8024446503, 1239164.8448687352, 0, 0], [5908531.852921399, 0, 2811734.0315504763, 1239164.8448687352, 0, 0], [5505496.227200101, 0, 2825085.5343320365, 1274388.3101402405, 0, 0]], [[5734687.774578399, 340470.24771224, 2797183.9482664294, 1212793.6540635112, 16707.060129314974, 16645.22574904105], [5344020.914235198, 340470.24771224, 2805949.1773722554, 1212793.654063511, 16707.060129314974, 16645.22574904105], [4883885.358525899, 396092.72374146, 2819247.6626532064, 1246400.0689715126, 18627.445965190636, 19090.507320129564]], [[5064321.216007499, 691144.15463426, 2797183.9482664294, 1212793.654063511, 36334.34163403275, 37003.756219756106], [4770113.548217899, 598270.0931958001, 2805995.1361419563, 1211814.4576708125, 36995.51313719162, 38091.851989965675], [4424050.8535007, 635968.9652505, 2817807.8457276328, 1247390.6205966934, 31362.42262387216, 30753.445354675805]], [[4652594.279461999, 819261.4312802802, 2797183.948266429, 1212793.654063511, 58297.50570034137, 60844.84298934877], [4310279.0431927, 838146.3347048401, 2804555.319216383, 1212805.0092959937, 49730.489795873145, 49754.790024511916], [4075333.7800682997, 791377.1488039, 2818080.94694748, 1247390.6205966936, 41734.21237593352, 40390.31077317224]], [[3909568.7244754997, 1371864.61649432, 2797855.0903582945, 1211825.8129032953, 69992.41180466491, 71161.75459712697], [4055232.5498909997, 934744.1266721401, 2797271.1295344085, 1212805.0092959935, 67015.94647959378, 67351.5537636325], [3506119.795928899, 1159739.1215302402, 2820270.4182953425, 1268111.7911551865, 63384.28242442112, 62469.06588070371]], [[3730427.3434622, 1312990.2750329203, 2798681.6557392315, 1212793.654063511, 91944.64717693723, 93402.74621203027], [3698918.8385253, 1098241.87516472, 2797114.8059132635, 1215657.5617780066, 80121.78925670171, 79842.64756643304], [3493271.534834999, 1015633.0862728601, 2819349.467055155, 1251284.145764494, 67317.80973037747, 65776.33381422982]], [[3210183.324437, 1638530.3050982798, 2795633.7664894117, 1215657.5617780066, 104974.72799544752, 106668.68312101142], [3270824.8902690997, 1369754.11844992, 2800043.833799877, 1217158.1158939532, 83968.2627952119, 81711.87504253746], [3261521.6613771995, 1124354.9286954603, 2825547.339430762, 1289263.4571286584, 81932.76024836535, 80538.55800034705]], [[3005568.9252120997, 1673400.7897807402, 2796731.893669998, 1215657.5617780066, 117632.1902002327, 118179.19010504786], [2910964.6734291003, 1534153.9528083606, 2814277.6128028464, 1271417.2664389762, 109115.2787229085, 108536.96930337205], [2954833.912704299, 1267950.9783498, 2817775.880836475, 1252784.6998804407, 94101.59329954744, 91860.73495991071]], [[2975211.4541850006, 1555073.0162508201, 2796787.3689757306, 1214715.7276942933, 131554.31834531703, 131834.1353830695], [2802633.3370061005, 1471011.00003406, 2805107.1753346547, 1218199.0885797408, 112738.90970373887, 110896.70424584203], [2736486.6206438, 1319305.66509576, 2811484.391972167, 1251743.7271946531, 110469.7893492736, 107527.83278312997]]]

horizon = "inc"
horizon = "trans"

##############################################################################

def bar_chart(cost_per_, N_START, filename):
    # コストデータを億単位に変換
    cost_per_ = cost_per_ / 1e4
    
    TC_direct = cost_per_[:, 0]
    TC_indirect = cost_per_[:, 1]
    IC_inc = cost_per_[:, 2]
    OC_inc = cost_per_[:, 3]
    IC_trans = cost_per_[:, 4]
    OC_trans = cost_per_[:, 5]

    plt.figure(figsize=(12, 6))
    N_FACILITY = np.arange(cost_per_.shape[0]) + N_START
    plt.xticks(N_FACILITY)
    plt.bar(N_FACILITY, TC_direct, color='blue', label='TC_direct')
    plt.bar(N_FACILITY, TC_indirect, bottom=TC_direct, color='blue', linestyle='--', label='TC_indirect')
    plt.bar(N_FACILITY, IC_inc, bottom=TC_direct + TC_indirect, color='orange', label='IC_inc')
    plt.bar(N_FACILITY, OC_inc, bottom=TC_direct + TC_indirect + IC_inc, color='orange', linestyle='--', label='OC_inc')
    plt.bar(N_FACILITY, IC_trans, bottom=TC_direct + TC_indirect + IC_inc + OC_inc, color='yellow', label='IC_trans')
    plt.bar(N_FACILITY, OC_trans, bottom=TC_direct + TC_indirect + IC_inc + OC_inc + IC_trans, color='yellow', linestyle='--', label='OC_trans')

    # 同色間点線の描画
    for x in range(cost_per_.shape[0]):
        adjusted_x = x + N_START  # 調整されたインデックス
        plt.hlines(TC_direct[x], adjusted_x - 0.4, adjusted_x + 0.4, colors='black', linestyles='dotted')
        plt.hlines(TC_direct[x] + TC_indirect[x] + IC_inc[x], adjusted_x - 0.4, adjusted_x + 0.4, colors='black', linestyles='dotted')
        plt.hlines(TC_direct[x] + TC_indirect[x] + IC_inc[x] + OC_inc[x] + IC_trans[x], adjusted_x - 0.4, adjusted_x + 0.4, colors='black', linestyles='dotted')

    # 凡例
    handles, labels = plt.gca().get_legend_handles_labels()
    # plt.legend(handles[::-1], labels[::-1], loc='upper left', bbox_to_anchor=(1.05, 1))        
    plt.legend(handles[::-1], labels[::-1], loc='lower left', bbox_to_anchor=(1, 0.4))        

    # ラベル
    plt.xlabel(xlabel)
    plt.ylabel('Cost (億円)')
    plt.title(f'Stacked Bar Chart for {title_suffix}')
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    
    # ファイルに保存
    plt.savefig(filename)
    plt.close()  # グラフを閉じる

if horizon == "inc":
    save_folder = f"graphs_{str(foldername)}_INC_{current_time}"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    for N_TRANS in range(len(cost)):
        cost_per_inc = np.array(cost[N_TRANS])
        title_suffix = f'N_TRANS = {N_TRANS}'
        xlabel = 'N_INC'
        filename = os.path.join(save_folder, f'TRANS{N_TRANS}.png')
        bar_chart(cost_per_inc, 1, filename)

if horizon == "trans":
    save_folder = f"graphs_{str(foldername)}_TRANS_{current_time}"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    transposed_cost = np.transpose(cost, (1, 0, 2))
    for N_INC in range(len(transposed_cost)):
        cost_per_trans = np.array(transposed_cost[N_INC])
        title_suffix = f'N_INC = {N_INC+1}'
        xlabel = 'N_TRANS'
        filename = os.path.join(save_folder, f'INC{N_INC+1}.png')
        bar_chart(cost_per_trans, 0, filename)
