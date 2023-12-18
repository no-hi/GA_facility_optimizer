import matplotlib.pyplot as plt
import numpy as np

cost = [[[3083869.9778700015, 0, 329899.8818864615, 138135.64307217477, 0, 0], [2201519.0800500005, 0, 342047.53477158566, 162512.92984408402, 0, 0], [1402573.0722900003, 0, 355771.4966967819, 205841.14094314096, 0, 0], [1038362.30988, 0, 370066.5367502598, 250846.51253793284, 0, 0], [831602.9737199997, 0, 383553.5011646385, 288363.6782075949, 0, 0], [646492.7377499996, 0, 397615.02799237816, 345332.6310899478, 0, 0], [510710.41811999993, 0, 407908.6272932413, 382365.82904059737, 0, 0]], [[2272390.8020699993, 198615.18181799995, 329899.8818864615, 138135.64307217477, 7653.720155424562, 538239.5382205871], [1369567.9353300005, 198615.18181799995, 342047.53477158566, 162512.92984408402, 7653.720155424562, 538239.5382205871], [1308970.0427400002, 28916.680626000005, 355856.3595257742, 206581.6678337846, 1158.9205813269793, 62306.97036175476], [1034909.40132, 1634.53944, 370066.5367502598, 250846.51253793284, 160.9236516894888, 7062.95509722004], [832710.2621699999, 0, 384110.53616400325, 307426.8108801027, 0, 0], [644601.1631999996, 630.2405100000001, 397615.02799237816, 345332.6310899478, 139.51646926533232, 6352.544853535483], [510330.9901199999, 20000.60496000000003, 407908.6272932413, 382365.82904059737, 50000.12293421063784, 20000.766374232437]]]

for N_TRANS in range(len(cost)):
    current_data = np.array(cost[N_TRANS])
    N_INC = np.arange(current_data.shape[0])

    TC_direct = current_data[:, 0]
    TC_indirect = current_data[:, 1]
    IC_inc = current_data[:, 2]
    OC_inc = current_data[:, 3]
    IC_trans = current_data[:, 4]
    OC_trans = current_data[:, 5]

    plt.figure(figsize=(12, 6))
    plt.bar(N_INC, TC_direct, color='blue', label='TC_direct')
    plt.bar(N_INC, TC_indirect, bottom=TC_direct, color='blue', linestyle='--', label='TC_indirect')
    plt.bar(N_INC, IC_inc, bottom=TC_direct + TC_indirect, color='orange', label='IC_inc')
    plt.bar(N_INC, OC_inc, bottom=TC_direct + TC_indirect + IC_inc, color='orange', linestyle='--', label='OC_inc')
    plt.bar(N_INC, IC_trans, bottom=TC_direct + TC_indirect + IC_inc + OC_inc, color='yellow', label='IC_trans')
    plt.bar(N_INC, OC_trans, bottom=TC_direct + TC_indirect + IC_inc + OC_inc + IC_trans, color='yellow', linestyle='--', label='OC_trans')

    # 同色間点線の描画
    for x in N_INC:
        plt.hlines(TC_direct[x], x - 0.4, x + 0.4, colors='black', linestyles='dotted')
        plt.hlines(TC_direct[x] + TC_indirect[x] + IC_inc[x], x - 0.4, x + 0.4, colors='black', linestyles='dotted')
        plt.hlines(TC_direct[x] + TC_indirect[x] + IC_inc[x] + OC_inc[x] + IC_trans[x], x - 0.4, x + 0.4, colors='black', linestyles='dotted')

    # 凡例
    plt.legend(loc='upper right', bbox_to_anchor=(1, 1))
    
    # ラベル
    plt.xlabel('N_INC')
    plt.ylabel('Cost')
    plt.title(f'Stacked Bar Chart for N_TRANS = {N_TRANS}')
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.show()
