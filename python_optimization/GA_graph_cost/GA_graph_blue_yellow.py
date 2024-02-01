import os
import matplotlib.pyplot as plt
import numpy as np
import GA_graph__input as input
import matplotlib
matplotlib.rcParams['font.family'] = 'TakaoPGothic' # takao インストール後、matplotlibのフォルダ行ってキャッシュ削除
import datetime
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
foldername = input.foldername
cost = input.cost

horizon = "inc"
######################
# horizon = "trans"
N_INC_THRESHOLD = 12  # 以上生成
N_TRANS_THRESHOLD = 0  # 以上生成
######################

def bar_chart(cost_per_, N_START, filename):
    # コストデータを億単位に変換
    cost_per_ = cost_per_ / 1e4
    
    TC_direct = cost_per_[:, 0]
    TC_indirect = cost_per_[:, 1]
    IC_trans = cost_per_[:, 4]
    OC_trans = cost_per_[:, 5]

    plt.figure(figsize=(12, 6))
    N_FACILITY = np.arange(cost_per_.shape[0]) + N_START
    plt.xticks(N_FACILITY)
    plt.bar(N_FACILITY, TC_direct, color='blue', label='TC_direct')
    plt.bar(N_FACILITY, TC_indirect, bottom=TC_direct, color='blue', linestyle='--', label='TC_indirect')
    plt.bar(N_FACILITY, IC_trans, bottom=TC_direct + TC_indirect, color='yellow', label='IC_trans')
    plt.bar(N_FACILITY, OC_trans, bottom=TC_direct + TC_indirect + IC_trans, color='yellow', linestyle='--', label='OC_trans')

    # 同色間点線の描画
    for x in range(cost_per_.shape[0]):
        adjusted_x = x + N_START  # 調整されたインデックス
        plt.hlines(TC_direct[x], adjusted_x - 0.4, adjusted_x + 0.4, colors='black', linestyles='dotted')
        plt.hlines(TC_direct[x] + TC_indirect[x] + IC_trans[x], adjusted_x - 0.4, adjusted_x + 0.4, colors='black', linestyles='dotted')

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
    save_folder = f"graphs__{str(foldername)}_INC_{current_time}"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    transposed_cost = np.transpose(cost, (1, 0, 2))
    for N_TRANS in range(len(transposed_cost)):
        cost_per_trans = np.array(transposed_cost[N_TRANS])
        # N_INC_THRESHOLD以上のデータのみを選択
        cost_per_trans = cost_per_trans[N_INC_THRESHOLD-1:]
        title_suffix = f'N_TRANS = {N_TRANS}'
        xlabel = 'N_INC'
        filename = os.path.join(save_folder, f'TRANS{N_TRANS}.png')
        bar_chart(cost_per_trans, N_INC_THRESHOLD, filename)

if horizon == "trans":
    save_folder = f"graphs__{str(foldername)}_TRANS_{current_time}"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    for N_INC in range(len(cost)):
        cost_per_inc = np.array(cost[N_INC])
        # N_TRANS_THRESHOLD以上のデータのみを選択
        cost_per_inc = cost_per_inc[N_TRANS_THRESHOLD-1:]
        title_suffix = f'N_INC = {N_INC+1}'
        xlabel = 'N_TRANS'
        filename = os.path.join(save_folder, f'INC{N_INC+1}.png')
        bar_chart(cost_per_inc, N_TRANS_THRESHOLD, filename)
