import os
import matplotlib.pyplot as plt
import numpy as np
import GA_graph__input as input
import matplotlib
matplotlib.rcParams['font.family'] = 'TakaoPGothic' # takao インストール後、matplotlibのフォルダ行ってキャッシュ削除
import datetime
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
foldername = input.foldername
energy = input.energy


horizon = "inc"
######################
# horizon = "trans"
######################

def bar_chart(energy_per_, N_START, filename):
    # コストデータを億単位に変換
    energy_per_ = energy_per_ / 1e4
    
    EL_direct = energy_per_[:, 0]/1000
    EL_indirect = energy_per_[:, 1]/1000
    ED_inc = energy_per_[:, 2]/1000
    ED_trans = energy_per_[:, 3]/1000

    plt.figure(figsize=(12, 6))
    N_FACILITY = np.arange(energy_per_.shape[0]) + N_START
    plt.xticks(N_FACILITY)
    
    # EL_directとEL_indirectをプロット
    plt.bar(N_FACILITY, EL_direct, color='orange', label='EL_direct')
    plt.bar(N_FACILITY, EL_indirect, bottom=EL_direct, color='orange', linestyle='--', label='EL_indirect')

    # ED_incの正の値と負の値を分ける
    ED_inc_positive = np.where(ED_inc > 0, ED_inc, 0)
    ED_inc_negative = np.where(ED_inc <= 0, ED_inc, 0)

    # ED_incの正の値をプロット
    plt.bar(N_FACILITY, ED_inc_positive, bottom=EL_direct + EL_indirect, color='yellow', label='ED_inc')

    # ED_incの負の値をプロット
    plt.bar(N_FACILITY, ED_inc_negative, color='yellow', label='ED_inc')

    # ED_transをプロット
    plt.bar(N_FACILITY, ED_trans, bottom=EL_direct + EL_indirect + ED_inc_positive, color='yellow', linestyle='--', label='ED_trans')


    # 同色間点線の描画
    for x in range(energy_per_.shape[0]):
        adjusted_x = x + N_START  # 調整されたインデックス
        plt.hlines(EL_direct[x], adjusted_x - 0.4, adjusted_x + 0.4, colors='black', linestyles='dotted')

    # 凡例
    handles, labels = plt.gca().get_legend_handles_labels()
    # plt.legend(handles[::-1], labels[::-1], loc='upper left', bbox_to_anchor=(1.05, 1))        
    plt.legend(handles[::-1], labels[::-1], loc='lower left', bbox_to_anchor=(1, 0.4))        

    # ラベル
    plt.xlabel(xlabel)
    plt.ylabel('energy (TJ/年)')
    plt.title(f'Stacked Bar Chart for {title_suffix}')
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    
    # ファイルに保存
    plt.savefig(filename)
    plt.close()  # グラフを閉じる

if horizon == "inc":
    save_folder = f"graphs__energy_{str(foldername)}_INC_{current_time}"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    transposed_energy = np.transpose(energy, (1, 0, 2))
    for N_INC in range(len(transposed_energy)):
        energy_per_trans = np.array(transposed_energy[N_INC])
        title_suffix = f'N_TRANS = {N_INC}'
        xlabel = 'N_INC'
        filename = os.path.join(save_folder, f'TRANS{N_INC}.png')
        bar_chart(energy_per_trans, 1, filename)

if horizon == "trans":
    save_folder = f"graphs__energy_{str(foldername)}_TRANS_{current_time}"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    for N_TRANS in range(len(energy)):
        energy_per_inc = np.array(energy[N_TRANS])
        title_suffix = f'N_INC = {N_TRANS+1}'
        xlabel = 'N_TRANS'
        filename = os.path.join(save_folder, f'INC{N_TRANS+1}.png')
        bar_chart(energy_per_inc, 0, filename)
