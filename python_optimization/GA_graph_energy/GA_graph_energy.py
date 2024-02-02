import os
import matplotlib.pyplot as plt
import numpy as np
import GA_graph___input as input
import matplotlib
matplotlib.rcParams['font.family'] = 'TakaoPGothic' # takao インストール後、matplotlibのフォルダ行ってキャッシュ削除
import datetime
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
foldername = input.foldername
energy = input.energy


horizon = "inc"
######################
# horizon = "trans"
N_INC_THRESHOLD = 1  # 以上生成
N_TRANS_THRESHOLD = 0  # 以上生成
######################

def bar_chart(energy_per_, N_START, filename):
    # エネルギー(GJ)をTJ単位に変換
    energy_per_ = energy_per_ / 1e3
    
    EL_direct = energy_per_[:, 0]
    EL_indirect = energy_per_[:, 1]
    ED_inc = energy_per_[:, 2]
    ED_trans = energy_per_[:, 3]

    plt.figure(figsize=(12, 6))
    N_FACILITY = np.arange(energy_per_.shape[0]) + N_START
    plt.xticks(N_FACILITY)
    plt.bar(N_FACILITY, EL_direct, color='orange', label='EL_direct')
    plt.bar(N_FACILITY, EL_indirect, bottom=EL_direct, color='orange', label='EL_indirect')
    ED_inc_positive = np.where(ED_inc > 0, ED_inc, 0)
    ED_inc_negative = np.where(ED_inc <= 0, ED_inc, 0)
    # ED_incの正の値と負の値をプロット（ラベルは一時的に異なるものを設定）
    plt.bar(N_FACILITY, ED_inc_positive, bottom=EL_direct + EL_indirect, color='yellow', label='ED_inc_positive')
    plt.bar(N_FACILITY, ED_inc_negative, color='yellow', label='ED_inc_negative')
    plt.bar(N_FACILITY, ED_trans, bottom=EL_direct + EL_indirect + ED_inc_positive, color='gray', label='ED_trans')

    # 同色間点線の描画
    for x in range(energy_per_.shape[0]):
        adjusted_x = x + N_START  # 調整されたインデックス
        plt.hlines(EL_direct[x], adjusted_x - 0.4, adjusted_x + 0.4, colors='black', linestyles='dotted')

    # 折れ線グラフを積み上げ棒グラフに重ねて表示
    total_energy = np.sum(energy_per_, axis=1)
    plt.plot(N_FACILITY, total_energy, color='blue', marker='o', linestyle='-', label='Total Energy')

    # 凡例の調整（折れ線グラフの凡例を追加）
    handles, labels = plt.gca().get_legend_handles_labels()
    new_labels, new_handles = [], []
    for handle, label in zip(handles, labels):
        if label.endswith('_positive') or label.endswith('_negative'):
            label = 'ED_inc'
        if label not in new_labels:
            new_labels.append(label)
            new_handles.append(handle)

    ordered_labels = ['ED_trans', 'EL_indirect', 'EL_direct', 'ED_inc', 'Total Energy']
    ordered_handles = [new_handles[new_labels.index(label)] for label in ordered_labels]

    plt.legend(ordered_handles, ordered_labels, loc='lower left', bbox_to_anchor=(1, 0.4))

    # ラベル
    plt.xlabel(xlabel)
    plt.ylabel('energy (TJ/年)')
    plt.title(f'Stacked Bar Chart for {title_suffix}')
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    
    # ファイルに保存
    plt.savefig(filename)
    plt.close()  # グラフを閉じる


if horizon == "inc":
    save_folder = f"graphs__energy_I{N_INC_THRESHOLD}~{str(foldername)}_{current_time}"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    transposed_energy = np.transpose(energy, (1, 0, 2))
    for N_TRANS in range(len(transposed_energy)):
        energy_per_trans = np.array(transposed_energy[N_TRANS])
        # N_INC_THRESHOLD以上のデータのみを選択
        energy_per_trans = energy_per_trans[N_INC_THRESHOLD-1:]
        title_suffix = f'N_TRANS = {N_TRANS}'
        xlabel = 'N_INC'
        filename = os.path.join(save_folder, f'TRANS{N_TRANS}.png')
        bar_chart(energy_per_trans, N_INC_THRESHOLD, filename)

if horizon == "trans":
    save_folder = f"graphs__energy_T{N_TRANS_THRESHOLD}~{str(foldername)}_{current_time}"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    for N_INC in range(len(energy)):
        energy_per_inc = np.array(energy[N_INC])
        # N_TRANS_THRESHOLD以上のデータのみを選択
        energy_per_inc = energy_per_inc[(N_TRANS_THRESHOLD-1)+1:]
        print(f"N_INC: {N_INC+1}, Selected data shape: {energy_per_inc.shape}")

        title_suffix = f'N_INC = {N_INC+1}'
        xlabel = 'N_TRANS'
        filename = os.path.join(save_folder, f'INC{N_INC+1}.png')
        bar_chart(energy_per_inc, N_TRANS_THRESHOLD, filename)
        
        
