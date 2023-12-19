import matplotlib.pyplot as plt
import numpy as np

import matplotlib
matplotlib.rcParams['font.family'] = 'TakaoPGothic'
# matplotlib.rcParams['font.family'] = 'IPAexGothic'

##############################################################################

cost = [[[29367854.78655, 0, 2758218.7167389826, 1154921.0445051813, 0, 0], [13860582.1635, 0, 2758218.716738983, 1154921.0445051813, 0, 0], [10462746.263639998, 0, 2758218.716738983, 1154921.0445051813, 0, 0], [7973559.464910001, 0, 2758218.716738983, 1154921.0445051813, 0, 0], [6463921.797659998, 0, 2758218.716738983, 1154921.0445051815, 0, 0], [5144775.544499999, 0, 2763666.6942516672, 1154921.0445051813, 0, 0], [4075861.613759997, 0, 2763666.694251667, 1154921.0445051813, 0, 0], [3450437.7089099973, 0, 2774502.662146316, 1168235.1904254048, 0, 0], [3059759.8289099974, 0, 2775575.7501606913, 1168235.1904254048, 0, 0], [2617576.5643799994, 0, 2790483.7194083408, 1211814.4576708127, 0, 0], [2393248.5304199997, 0, 2790483.7194083408, 1211814.4576708127, 0, 0], [2171240.79279, 0, 2797183.9482664294, 1212793.6540635112, 0, 0], [2037603.3263100001, 0, 2805949.1773722554, 1212793.654063511, 0, 0]], [[12687280.79292, 5378872.414032, 2758218.7167389826, 1154921.0445051813, 124339.14552753954, 11144129.13613678], [13801357.33374, 37223.03016, 2758218.716738983, 1154921.0445051813, 1620.9206162807732, 91350.56895956438], [9367451.031809999, 465989.64706200006, 2758218.7167389826, 1154921.0445051815, 9114.219744395892, 653688.0343107076], [7006712.640299997, 296727.70578600006, 2758218.7167389826, 1154921.0445051813, 7654.642153586334, 538240.3822618506], [5687566.38714, 296727.70578600006, 2763666.6942516672, 1154921.0445051813, 7654.642153586334, 538240.3822618506], [5144727.981299999, 3322.24932, 2763666.6942516672, 1154921.0445051813, 577.956419079326, 27606.74837798279], [4070400.015869997, 2791.5577500000004, 2763666.694251667, 1154921.0445051813, 331.988604865138, 14855.59142091406], [3444976.1110199974, 2791.5577500000004, 2774502.662146316, 1168235.1904254048, 331.988604865138, 14855.59142091406], [3008254.444379998, 0, 2789410.6313939663, 1211814.4576708127, 0, 0], [2617576.5643799994, 0, 2790483.7194083408, 1211814.4576708127, 0, 0], [2393248.5304199997, 0, 2790483.7194083408, 1211814.4576708127, 0, 0], [2171240.79279, 0, 2797183.9482664294, 1212793.6540635112, 0, 0], [2032417.1462400004, 2650.3702140000005, 2805854.7721224804, 1212793.654063511, 331.988604865138, 14855.59142091406]], [[12403175.213640003, 4983698.278476001, 2758218.7167389826, 1154921.0445051813, 129459.06964296915, 11312670.269681143], [12751399.804919995, 432471.75256799994, 2758218.716738983, 1154921.0445051813, 9989.63823161675, 666415.5843230635], [9353563.905059999, 432471.75256799994, 2758218.716738983, 1154921.0445051813, 9989.63823161675, 666415.5843230635], [6910513.7304599965, 359313.7763100001, 2758218.716738983, 1154921.0445051815, 9402.528516760605, 622509.5802107297], [5948153.583539999, 157777.46691, 2758218.716738983, 1154921.0445051815, 7338.865479149159, 474485.40770968766], [5021285.510699998, 70555.03788, 2763666.694251667, 1154921.0445051813, 3258.452567438281, 188355.78786741773], [4075814.050559997, 1976.48457, 2763666.694251667, 1154921.0445051813, 654.3973830524246, 29006.751435621347], [3441613.1514299973, 4570.92642, 2774502.662146316, 1168235.1904254048, 695.6334202570251, 31129.68187081626], [3050935.2714299974, 4570.92642, 2775575.7501606913, 1168235.1904254048, 695.6334202570251, 31129.68187081626], [2608752.006899999, 4570.92642, 2790483.7194083408, 1211814.4576708127, 695.6334202570251, 31129.68187081626], [2383913.5921499995, 5340.105041999999, 2790268.106690171, 1210041.7301478935, 645.629525380996, 31150.779980249506], [2162416.2353099994, 4570.92642, 2797183.9482664294, 1212793.6540635112, 695.6334202570251, 31129.68187081626], [2046770.2764900003, 795.71592, 2805365.356362826, 1212793.654063511, 480.1470422914266, 22644.780477114567]], [[12403175.213640003, 4838617.380468001, 2758218.7167389826, 1154921.0445051813, 132427.30117294015, 11314770.388410402], [12668738.035649996, 473246.7660419999, 2758218.716738983, 1154921.0445051813, 11452.54739184131, 737243.2594712108], [9270902.135789998, 473246.7660419999, 2758218.7167389826, 1154921.0445051813, 11452.54739184131, 737243.2594712108], [6875014.695749999, 354050.85646799987, 2758218.7167389826, 1154921.0445051813, 10230.150501375134, 667815.5939435542], [6494042.004090001, 2772.20049, 2763666.694251667, 1154921.0445051813, 1134.5444253438513, 51651.53191273591], [4625744.86053, 145535.290866, 2763666.6942516672, 1154921.0445051813, 7771.746869658853, 479437.2609608337], [3556830.929789998, 145535.290866, 2763666.694251667, 1154921.0445051813, 7771.746869658853, 479437.2609608337], [2923919.430839998, 134436.795234, 2774606.5870801434, 1169093.069198798, 7931.718230596193, 490765.76702708536], [2965738.3444199977, 20220.37623, 2789753.1753920317, 1211732.259117882, 1623.0580511636083, 82127.20373766452], [2607491.6465399987, 4822.998492000001, 2790483.7194083408, 1211814.4576708127, 1059.6360626740284, 47403.983336127436], [2373465.1603199993, 7022.220546, 2790556.2819698164, 1212413.1978033301, 1413.4010818711995, 65823.7902949474], [2171140.9401299995, 5101.617990000001, 2796600.127257, 1212793.6540635112, 941.6012344712132, 43880.83882788499]], [[11548209.81816, 5008803.956004, 2758218.7167389826, 1154921.0445051813, 139811.89170009544, 11826816.83534361], [12521290.874159995, 504761.7696359999, 2758218.7167389826, 1154921.0445051813, 13350.139169014757, 871070.3503058407], [9123454.974299999, 504761.7696359999, 2758218.7167389826, 1154921.0445051813, 13350.139169014757, 871070.3503058407], [6776425.1335499985, 397693.936158, 2758218.716738983, 1154921.0445051815, 11802.544490982065, 753510.1753379441], [5928630.286589999, 138328.61760599999, 2758218.716738983, 1154921.0445051815, 8281.650289223544, 502793.2960199841], [4609484.03343, 142885.986006, 2763666.6942516672, 1154921.0445051813, 8277.621146617043, 502793.29585881846], [3540570.1026899978, 138328.61760599999, 2763666.694251667, 1154921.0445051813, 8281.650289223544, 502793.2960199841], [2923919.430839998, 130768.22267999999, 2774606.5870801434, 1169093.069198798, 8119.3364509267585, 491465.77453181415], [2533241.550839999, 130768.22267999999, 2775679.675094518, 1169093.069198798, 8119.3364509267585, 491465.77453181415], [2550105.360869999, 19650.44388, 2790483.7194083408, 1211814.4576708127, 2698.8766369176856, 138754.06069259974], [2389029.6280799992, 8645.241984, 2789684.285680741, 1210041.7301478935, 1545.020733841933, 70765.22210822662], [2103769.58928, 19962.208872000003, 2797334.3378462777, 1212765.1935028508, 2614.263705962797, 137354.05730808247]], [[11548209.81816, 5001596.288688001, 2758218.7167389826, 1154921.0445051813, 140781.09604085062, 11828216.874111786], [12521290.874159995, 500893.72183799994, 2758218.7167389826, 1154921.0445051813, 13625.96069217092, 872470.3613387016], [9123454.974299999, 500893.72183799994, 2758218.7167389826, 1154921.0445051813, 13625.96069217092, 872470.3613387016], [6776425.1335499985, 395980.07368200005, 2758218.716738983, 1154921.0445051815, 11979.619298698979, 754910.1824209364], [5921619.446429999, 153155.27527199997, 2758218.716738983, 1154921.0445051815, 8649.700821717564, 516943.8951907726], [4602473.19327, 153155.27527199997, 2763666.6942516672, 1154921.0445051813, 8649.700821717564, 516943.8951907726], [3517298.435429998, 147680.26371600002, 2763666.694251667, 1154921.0445051813, 9024.17473514658, 539599.9248327429], [2923919.430839998, 130768.22267999999, 2774606.5870801434, 1169093.069198798, 8119.3364509267585, 491465.77453181415], [2533241.550839999, 129441.79909199999, 2775679.675094518, 1169093.069198798, 8250.238119642174, 492865.7797678809], [2612015.1138299988, 6547.41099, 2789899.8983989116, 1211814.4576708127, 1350.0308033094498, 60136.43330643761], [2331442.1924099997, 27348.49803, 2797526.492264495, 1212711.4555105804, 2842.551879322089, 138029.09797659572], [2150149.8870899994, 5917.419312, 2797183.9482664294, 1212793.6540635112, 1690.5596711874239, 76408.34248704439]]]
horizon = "inc"
horizon = "trans"

##############################################################################

def bar_chart(cost_per_,N_START):
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
    plt.show()

if horizon == "inc":
    for N_TRANS in range(len(cost)):
        cost_per_inc = np.array(cost[N_TRANS])
        title_suffix = f'N_TRANS = {N_TRANS}'
        xlabel = 'N_INC'
        bar_chart(cost_per_inc,1)

if horizon == "trans":
    transposed_cost = np.transpose(cost, (1, 0, 2))
    for N_INC in range(len(transposed_cost)):
        cost_per_trans = np.array(transposed_cost[N_INC])
        title_suffix = f'N_INC = {N_INC}'
        xlabel = 'N_TRANS'
        bar_chart(cost_per_trans,0)
