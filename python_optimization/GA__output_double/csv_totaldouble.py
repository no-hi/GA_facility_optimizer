import csv
import os

# 提供されたリストデータ
#inc[1~10]&trans[0~10]
foldername = "kanen42.68"
totaldouble = [[9886868.721911257, 8312754.759655518, 6814793.722876256, 6089939.461731113, 5713858.740344714, 5339203.328753996, 5038807.801584733, 4888523.356781473, 4774846.423838645, 4701187.25357518, 4640915.27227517], [7202564.449746762, 5704603.412967498, 5027796.263201484, 4747038.934854917, 4447036.647230249, 4196109.894463539, 4045590.6419272125, 3925205.174766099, 3851546.0045026345, 3791274.0232026237, 3732645.860450534], [4908980.739055801, 4232173.589289788, 3933955.3305720906, 3651413.9733185526, 3393543.8786004907, 3243851.8734707735, 3130174.940527946, 3069902.9592279373, 3011274.796475846, 2965029.6414533993, 2922748.273648278], [3931941.785568873, 3629705.6120388275, 3329698.3775181216, 3112025.085724203, 2953975.5612952197, 2854609.844794991, 2794369.5008750693, 2749413.214167618, 2705842.978047502, 2672324.588838165, 2638961.374130375], [3497272.407399424, 3199827.1009247336, 2979417.723948346, 2829397.239432733, 2730031.5229325043, 2671034.1534322235, 2616805.852391761, 2582507.630604655, 2548986.9799390817, 2518517.0915550115, 2490279.781759387], [3169191.752064213, 2871746.445589521, 2721725.9610739085, 2622360.244573679, 2563362.8750733985, 2563648.220313212, 2474836.3522458305, 2441293.072015218, 2413048.7092963075, 2387150.393882866, 2366749.3549939482], [2837100.5797507586, 2668568.32899536, 2588900.757460059, 2510205.2429948496, 2455976.941954387, 2421678.720167281, 2407407.431668788, 2360146.2922072904, 2353264.753536436, 2332863.7146475185, 2314840.198483768], [2704275.3761369092, 2535743.1253815102, 2476745.75588123, 2422517.4548407677, 2388706.427445865, 2354408.2056587595, 2326260.65186086, 2305859.612971943, 2287675.3669981137, 2270519.4307970456, 2256273.6843044655], [2558031.0658733575, 2503802.764832895, 2456951.2160158195, 2385924.905000191, 2389425.031258051, 2323966.32380739, 2305782.077833561, 2288626.1416324917, 2276440.091715103, 2262912.2647245647, 2249600.523827076], [2521438.516032781, 2467210.214992319, 2420358.6661752425, 2387130.7032045806, 2334929.8789088386, 2306782.325110939, 2288598.07913711, 2271442.142936041, 2268832.925642623, 2243884.6555459737, 2233228.760171961]]


# CSVファイル名
current_directory = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(current_directory, 'total_double_matrix.csv')

# CSVファイルに書き込む
with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(totaldouble)