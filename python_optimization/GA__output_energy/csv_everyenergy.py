import csv
import os

# 提供されたリストデータ
every_energy = [[[807374.2928173541, 0, -638470.089784596, 0], [468699.7992790207, 210827.69373959588, -638470.089784596, 9655.693150684932], [256250.0428369376, 302597.13284435053, -638470.089784596, 15080.309260273974], [126825.63271516668, 371918.8189176264, -638470.089784596, 21233.65808219178], [125935.74176922918, 342930.96011192433, -638470.089784596, 21266.373698630137], [125935.74176922918, 311561.5063693861, -638470.089784596, 21266.373698630137], [48803.07786358334, 362201.4301968294, -638470.089784596, 27200.55846575342], [47086.04224945834, 351093.4148386407, -638470.089784596, 27304.208876712328], [47971.642864708345, 340453.5708249999, -638470.089784596, 27269.658739726023], [47351.68747670834, 334167.92260365596, -638470.089784596, 27304.881534246575], [38947.647593562506, 336907.9378527592, -638470.089784596, 28001.93819178082], [38947.647593562506, 332663.1497548212, -638470.089784596, 28001.93819178082], [27107.981922666673, 338243.0912396619, -638470.089784596, 30107.600876712328], [15381.558262958333, 344190.1320738445, -638470.089784596, 32067.174575342466], [15381.558262958333, 340726.24604074337, -638470.089784596, 32067.17457534247], [14597.105176875, 338086.04306962114, -638470.089784596, 32099.523287671233], [14597.105176875, 335974.3112137295, -638470.089784596, 32099.52328767123], [7566.934309458334, 339558.15664954734, -638470.089784596, 33292.02279452055], [7566.934309458334, 337602.13991331105, -638470.089784596, 33292.02279452055], [7503.434974208334, 335989.95465147676, -638470.089784596, 33294.28536986301], [7503.434974208334, 334060.9350526284, -638470.089784596, 33294.285369863006]], [[571010.2506222291, 0, -496650.2048550757, 0], [358560.4941801461, 91769.43910475464, -496650.2048550757, 5424.616109589041], [135466.56093316668, 280149.37981287186, -527745.8796818317, 15809.041972602741], [134576.6699872292, 251161.52100716947, -527745.8796818317, 15841.757589041095], [134576.6699872292, 219792.06726463127, -527745.8796818317, 15841.757589041095], [57444.00608158333, 270431.99109207455, -527745.8796818317, 21775.942356164385], [56702.39969739583, 258393.19373723483, -527852.1736627761, 21825.719013698632], [57588.00031264583, 247753.349723594, -527852.1736627761, 21791.168876712327], [49183.960429499995, 250493.36497269713, -527852.1736627761, 22488.225534246572], [49183.960429499995, 246248.57687475925, -527852.1736627761, 22488.225534246572], [37344.29475860417, 251828.5183595999, -527852.1736627761, 24593.88821917808], [25617.871098895837, 257775.55919378242, -527852.1736627761, 26553.46191780822], [25617.871098895837, 254311.67316068144, -527852.1736627761, 26553.461917808218], [24833.4180128125, 251671.47018955927, -527852.1736627761, 26585.810630136984], [23366.44462154167, 250438.4330063676, -528396.6942259534, 26674.90717808219], [16336.273754125003, 254022.27844218543, -528396.6942259534, 27867.406684931506], [16336.273754125003, 251910.54658629379, -528396.6942259534, 27867.406684931506], [16336.273754125003, 249954.52985005744, -528396.6942259534, 27867.406684931506], [16336.273754125003, 248025.51025120914, -528396.6942259534, 27867.406684931506], [12901.325749541667, 249461.77647146594, -528289.3418051249, 28083.268602739725], [12901.325749541667, 248494.25457216962, -528289.3418051249, 28083.268602739725]], [[367201.42239814607, 0, -385925.9947523115, 0], [245595.80533935415, 65364.301356460164, -386790.09271825297, 5950.022794520549], [183937.3536750209, 103006.09431208635, -388755.139302167, 10072.068164383563], [106804.689769375, 153646.0181395295, -388755.139302167, 16006.25293150685], [133915.90489902085, 219792.06726463127, -520997.1785662664, 15841.757589041095], [56783.24099337501, 270431.99109207455, -520997.1785662664, 21775.942356164385], [56041.63460918751, 258393.19373723483, -521106.323113203, 21825.719013698632], [56927.235224437514, 247753.349723594, -521106.323113203, 21791.168876712327], [48523.19534129168, 250493.36497269713, -521106.323113203, 22488.225534246572], [48523.19534129168, 246248.57687475925, -521106.323113203, 22488.225534246572], [47267.28217981251, 247206.83908026156, -524581.5534928589, 22654.18849315068], [35427.616508916675, 252786.78056510226, -524581.5534928589, 24759.851178082186], [23701.19284920834, 258733.82139928473, -524581.5534928589, 26719.424876712328], [24172.65292460417, 251671.47018955927, -521106.323113203, 26585.810630136984], [30264.42693435417, 250438.4330063676, -526286.716978619, 26674.90717808219], [22705.679533333332, 248326.70115047594, -521665.44723079266, 26674.90717808219], [15675.50866591667, 251910.54658629379, -521665.44723079266, 27867.406684931506], [15675.50866591667, 249954.52985005744, -521665.44723079266, 27867.406684931506], [14419.5955044375, 250912.7920555598, -525131.941727326, 28033.369643835613], [10866.044792145833, 251563.97355519945, -523969.84615774476, 28242.504986301366], [10921.148164604167, 250736.87301398232, -525023.4324757329, 28251.4941369863]], [[366540.65730993776, 0, -379177.2936367461, 0], [244935.04025114584, 65364.301356460164, -380041.3916026876, 5950.022794520549], [167949.09720549997, 116004.22518390337, -380369.20749221224, 11884.207561643836], [106143.92468116668, 153646.0181395295, -382006.4381866016, 16006.25293150685], [133678.81312554167, 219792.06726463127, -516756.5418576468, 15841.757589041095], [56546.14921989585, 270431.99109207455, -516756.5418576468, 21775.942356164385], [55804.54283570835, 258393.19373723483, -516867.3118758253, 21825.719013698632], [56690.143450958356, 247753.349723594, -516867.3118758253, 21791.168876712327], [51969.95131575002, 251291.8130275843, -521264.34719462617, 22166.26717808219], [42611.18181179168, 255009.9294800503, -521264.34719462617, 22981.161205479453], [33129.05849689584, 251141.64710011423, -507325.05660835834, 24544.111561643833], [31726.24576170834, 255366.98166359027, -521264.34719462617, 24968.986520547944], [31878.886872625004, 254094.53328757762, -519855.4359558423, 26542.882849315072], [18863.976591687504, 258963.65857841476, -521172.4416918469, 27024.016438356164], [18079.523505604167, 256323.4556072926, -521172.4416918469, 27056.365150684927], [29562.72252077084, 248326.70115047594, -520885.4679321995, 26674.90717808219], [10671.506485250002, 257634.8190890521, -521729.08685366745, 28267.0264109589], [10671.506485250002, 255523.08723316045, -521729.08685366745, 28267.0264109589], [10718.224757229167, 253492.9931540478, -521820.99235644675, 28242.504986301366], [13163.376486000001, 246413.32498937484, -510095.91377452674, 27869.66926027397], [10608.007150000001, 250025.8656362415, -521729.08685366745, 28269.288986301366]], [[366303.56553645857, 0, -374936.6569281265, 0], [244697.94847766665, 65364.301356460164, -375800.754894068, 5950.022794520549], [134099.5055326875, 280149.37981287186, -515800.3521986414, 15809.041972602741], [133209.61458675, 251161.52100716947, -515800.3521986414, 15841.757589041095], [72922.76871289584, 145603.69938209766, -356306.938829102, 17382.57139726027], [72181.16232870833, 133564.90202725798, -356413.23281004623, 17432.348054794522], [64599.22372556249, 135703.7092215848, -356413.23281004623, 18097.11715068493], [64412.00471658335, 216564.4420359355, -457759.65104802273, 22753.680657534245], [41033.13439495834, 147230.69154060798, -356413.23281004623, 22162.353534246573], [54036.0480489375, 221146.32038431396, -465553.95850928576, 23615.35495890411], [42370.116277666675, 250900.56229249257, -520783.8149407684, 22958.780054794515], [31183.007399645838, 331313.5958588322, -599405.3619284637, 29325.36131506849], [20268.065731062496, 340647.38464640884, -598897.2092359749, 31215.77358904109], [18804.026947062503, 258963.65857841476, -520783.8149407684, 27024.016438356168], [18019.57386097917, 256323.4556072926, -520783.8149407684, 27056.365150684927], [17641.727708041664, 254050.97365323425, -521340.46010258904, 27074.526904109585], [17381.31903435416, 330291.20409855264, -601631.7619732532, 31443.070684931503], [10611.556840625, 255523.08723316045, -521340.46010258904, 28267.0264109589], [12991.794659458335, 248025.51025120914, -507166.23764558905, 27867.40668493151], [10548.057505375, 251954.8852350898, -521340.46010258904, 28269.288986301366], [12747.89157985417, 229326.78144981136, -465769.8975451335, 29654.96350684932]], [[341443.2138111045, 0, -341594.404048937, 0], [191920.88954106253, 70570.90477286851, -309850.7678140851, 6153.348821917809], [116611.94906075003, 119628.88462508105, -309850.7678140851, 12005.469369863014], [133177.14323116667, 251161.52100716947, -515024.548915841, 15841.757589041095], [133177.14323116667, 219792.06726463127, -515024.548915841, 15841.757589041095], [56044.47932552085, 270431.99109207455, -515024.548915841, 21775.942356164385], [66832.725376625, 133222.48123583532, -350171.1927582184, 17954.819506849315], [56188.473556583354, 247753.349723594, -515135.77235869016, 21791.168876712327], [47784.43367343752, 250493.36497269713, -515135.7723586901, 22488.225534246572], [42446.31394683335, 255005.9787323013, -519196.33671448455, 22934.625534246574], [42887.69065533334, 325495.33323511743, -598757.1212464252, 27203.4325479452], [30938.33443891667, 256589.0835473961, -519087.19216754794, 24883.620164383563], [27832.95897822917, 230070.64621128028, -458519.8521125603, 27823.37819178082], [19098.668768020838, 258705.13899913576, -519087.19216754794, 26989.28284931507], [18537.148238645834, 334406.30615054443, -598757.1212464252, 31301.01764383562], [20298.805847666667, 225563.47356267396, -424291.2828005403, 27634.116821917814], [16736.639585791676, 251621.208026346, -482997.61526827, 31449.308054794517], [10624.255174541668, 255930.58321750828, -519755.4608320743, 28245.134465753425], [14855.065306250004, 229226.03844711123, -458583.93803340755, 29508.14071232877], [14855.065306250004, 227816.76251031953, -458583.93803340755, 29508.140712328768], [17417.72538241667, 225634.74700662994, -458996.74403302325, 28693.246684931513]], [[257676.82068456258, 0, -239048.28140099917, 0], [163241.63779760417, 61022.63257269183, -268730.58819595334, 5796.534575342466], [87932.69731729169, 110080.61242490436, -268730.58819595334, 11648.655123287672], [105405.16301331253, 153646.0181395295, -376033.8085361762, 16006.25293150685], [77489.62019012503, 190742.03617147024, -377941.7807569248, 17176.921643835616], [67525.43226893751, 230588.19453347166, -449825.57537334, 22437.898520547948], [57983.34279995835, 339584.3329615491, -586712.2516899081, 26119.108602739725], [54539.868940375, 138802.42272067597, -347702.02373065864, 20060.482191780822], [50007.25198489584, 233857.95566537298, -453333.5387874217, 23520.38794520548], [44235.96008297917, 225977.15887609628, -458194.04661886604, 25428.1058630137], [27902.983570854172, 221284.71403425818, -403051.2764821088, 25803.876821917806], [29840.366346374998, 253530.83864928075, -504011.4969338793, 24690.139397260275], [13912.311671645837, 271492.8956725851, -471960.0002415707, 31419.405369863012], [17157.053452770837, 245492.81735946063, -456385.136868323, 28426.87430136986], [14674.227273604174, 236707.7539500982, -458458.04479979514, 29508.140712328768], [12372.320433416668, 254022.27844218543, -504812.27874773496, 27867.406684931506], [13694.687369187506, 235534.0690030683, -459184.41596668557, 29538.532602739724], [16939.33964422917, 229219.0978241428, -458689.22785565513, 28677.46980821918], [16828.85100541667, 256426.66391729607, -482668.6094239754, 30165.388273972603], [11220.426449375, 247814.2454416135, -501607.7776834223, 27852.91397260274], [13566.689216708335, 229193.43132226658, -461076.8429066199, 29623.042849315076]], [[342785.1457823544, 0, -342336.2442158481, 0], [163156.52450256253, 61022.63257269183, -267217.57065416075, 5796.534575342466], [87847.58402225001, 110080.61242490436, -267217.57065416075, 11648.655123287672], [87105.97763806251, 98041.8150700647, -267323.86463510507, 11698.431780821918], [77363.25280612503, 190742.03617147024, -376066.7020426359, 17176.921643835616], [67593.53527685419, 137356.04809926127, -344991.88941232784, 17110.20624657534], [53239.386053479175, 258176.053864131, -501606.11818543816, 21815.139945205483], [56363.96745714584, 226166.55136428165, -457614.4336823291, 23421.568438356164], [55744.012069145836, 219880.90314293784, -457614.4336823291, 23456.791232876712], [53654.21311033334, 185511.0414871652, -378438.6208043346, 20225.466739726027], [41927.789450625, 191458.0823213477, -378438.6208043347, 22185.04043835616], [27442.982638229172, 218044.7264077375, -400441.3912157003, 25803.87682191781], [26562.91331985417, 218652.5781602195, -402902.97906862694, 25948.0701369863], [19532.742452437506, 222236.42359603735, -402902.97906862694, 27140.569643835617], [19638.216967687502, 256365.19493961125, -483053.71415017376, 31166.975342465757], [9764.558739812503, 247534.8948487913, -452909.55903350137, 29619.373808219178], [11683.881495270834, 224371.0547796487, -403630.92966375203, 27952.895342465752], [16849.073937312503, 220629.254391273, -404995.95015443966, 27492.308383561645], [11846.953512875003, 262279.0273392271, -471987.66006396903, 31786.43178082192], [14188.789279166667, 223040.5400331679, -411763.567204146, 28939.50049315069], [11572.544260875004, 220735.11545656118, -403462.45294929785, 28196.45852054795]], [[257216.94036837507, 0, -234827.42479148667, 0], [163030.15711856252, 61022.63257269183, -265342.4919398718, 5796.534575342466], [115873.18739289588, 119628.88462508105, -303878.1381636597, 12005.469369863014], [76000.8142104792, 138182.90051686042, -302517.3070231993, 14203.102684931506], [74612.95095475, 142088.6245922303, -343264.50613094453, 17182.975561643834], [65968.03435950002, 233858.063696985, -453958.71912439424, 22607.591671232876], [58848.6421144375, 213904.572742252, -395549.65381435247, 21038.648547945202], [58028.85665118751, 180108.69429058983, -353482.04522530764, 17921.00317808219], [58541.05493031251, 179356.62618832165, -358734.06987342256, 18035.416109589038], [38807.08245239582, 215337.67320007563, -395549.65381435247, 23844.303123287667], [26125.929171875003, 222256.08260668354, -395549.65381435247, 25921.71419178082], [27080.658792687507, 218044.7264077375, -396094.4814897187, 25803.87682191781], [29855.444532062495, 221208.71489366863, -408417.1245480844, 26149.683945205477], [15439.728663937502, 248950.09017606004, -445763.71238598827, 28546.974246575344], [15469.773867437503, 228544.77838393272, -408511.48281797924, 28789.375561643832], [16344.96622741667, 222016.00026845187, -399445.65462152706, 27605.68175342466], [16344.96622741667, 220059.98353221553, -399445.65462152706, 27605.68175342466], [7934.230133104166, 246728.4738429571, -446649.13799900934, 30139.21578082192], [18110.717396687498, 198592.652948393, -377324.05623112986, 24579.640109589043], [14961.907616770837, 220911.8640513893, -406500.14865450445, 27754.40021917809], [11269.067963291665, 230800.08644888859, -428684.80769385904, 29094.82323287672]], [[336099.5591511461, 0, -330471.8428540141, 0], [162816.9561571042, 61022.63257269183, -263213.2520183543, 5796.534575342466], [169313.4611087291, 89828.89495275581, -337165.11264593806, 11025.957698630136], [86766.40929260418, 98041.8150700647, -263319.54599929857, 11698.431780821918], [84850.98170900004, 91555.31421620135, -259567.8297572576, 11742.521424657534], [75990.0300547917, 184148.35866570417, -372590.86276675155, 17210.43221917808], [58573.709138750004, 195786.83871725976, -371337.8474316091, 20524.615890410958], [60301.94022341667, 180108.69429058983, -355364.0074694703, 17921.00317808219], [55681.603041458344, 179356.62618832165, -351892.7818985506, 18035.416109589038], [40186.64817374999, 216698.81583874323, -399217.0703776131, 23909.67320547945], [26505.16032070834, 221284.71403425818, -392757.17464684485, 25803.876821917806], [26505.16032070834, 218044.7264077375, -393308.39731635543, 25803.87682191781], [29955.513440666662, 220013.7207988871, -405052.2519469264, 26013.440219178083], [29578.191820395845, 200364.2458901243, -367988.7890834697, 24120.581917808224], [22425.340165583333, 226546.15193547783, -408740.80324579275, 27608.31123287671], [20315.947699937504, 220222.5440597823, -402298.4366817003, 27216.396493150685], [17208.557457000003, 222426.34510369215, -401585.82317355747, 27637.72471232877], [20216.033471291667, 210828.26502051373, -390828.8830707927, 27148.947287671235], [14528.950252916673, 252969.05235231057, -479414.5249956584, 32166.17753424658], [10704.269285395836, 225240.06143459157, -406449.2230787976, 29057.460164383563], [15544.038759708337, 220079.45726979335, -402836.8811608605, 27838.237808219186]]]


# CSVファイル名
current_directory = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(current_directory, 'every_energy_matrix.csv')

# 二次元リストに変換する関数
def flatten_3d_list_to_2d(three_d_list):
    two_d_list = []
    for sublist1 in three_d_list:
        for sublist2 in sublist1:
            two_d_list.append(sublist2)
    return two_d_list

# 三次元リストを二次元リストに変換
flattened_list = flatten_3d_list_to_2d(every_energy)

# CSVファイルに書き込む
with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(flattened_list)