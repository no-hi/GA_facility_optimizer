from deap import base, creator, tools, algorithms
import os
import sys
import random
import numpy as np
import time
import datetime
import collections
import data
start_time = time.perf_counter()
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
script_name = os.path.splitext(os.path.basename(__file__))[0]
output_directory_name = f"{script_name}_{current_time}"
current_directory = os.path.dirname(os.path.abspath(__file__))
output_directory = os.path.join(current_directory, output_directory_name)
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# ツールボックス使用宣言
toolbox = base.Toolbox()
# インポート
hokkaido = data.name
waste = data.kanen
distance = data.distance
# 2次元距離リスト生成
distance = np.array(distance).reshape(len(hokkaido), len(hokkaido))

# パラメータ
N_CITIES = len(hokkaido)   # 市町村数
N_FACI_MAX = 15            # 施設数上限
TOP_N_CITIES = 20          #ごみ量順位下限
N_IND = 150                # 個体数
N_GEN = 70                # 世代数
CX_PROB = 0.8              # 一様交叉
MUT_PROB = 0.3             # 突然変異
TOUR_SIZE = 4              # トーナメント
toolbox.register("select", tools.selTournament, tournsize=TOUR_SIZE)

# 最小化
creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) 
creator.create("Individual", list, fitness=creator.FitnessMin)

def get_top_cities(waste, top_n=TOP_N_CITIES):
    # ごみ量上位N個
    return sorted(range(len(waste)), key=lambda i: waste[i], reverse=True)[:top_n]


# GA施設数ループ##################################################
def GA_count(N_FACILITIES):
    original_stdout = sys.stdout
    with open(os.path.join(output_directory, f"output_{N_FACILITIES}.txt"), 'a', encoding="utf-8") as f:  # 追記モードで開く
        sys.stdout = f
        start_time_count = time.perf_counter()
        print("\n------------------  施設数: " + str(N_FACILITIES) +"  ------------------\n")
        print("個体数＝"+ str(N_IND))
        print("世代数＝"+ str(N_GEN))
        
        # 個体、個体群
        top_cities = get_top_cities(waste, top_n=TOP_N_CITIES)
        toolbox.register("indices", random.sample, top_cities, N_FACILITIES)
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # 一様交叉
        def cxSet(ind1, ind2):
            # 一様交叉
            temp1, temp2 = ind1[:], ind2[:]
            for i in range(len(temp1)):
                if random.random() < CX_PROB:
                    temp1[i], temp2[i] = temp2[i], temp1[i]
            
            # 重複修正
            # 1.「collections.Counter(ind)」でindの各要素の出現回数をカウント　　ind = [1, 2, 2, 3, 3, 3]　→　Counter({3: 3, 2: 2, 1: 1})を得る
            # 2.「.items()」でCounter({3: 3, 2: 2, 1: 1})をリスト化　　→　[(1, 1), (2, 2), (3, 3)]
            # 3.item,countリストを確認し、count > 1　となるitemをdupulicateとして取り出す
            # 4.重複dupulicateに対し、dupのcity以外をmissingとし、dupから重複分をpop削除しmissingを代わりに入力
            def repair(ind):
                duplicates = [item for item, count in collections.Counter(ind).items() if count > 1]
                missing = list(set(range(N_CITIES)) - set(ind))
                for dup in duplicates:
                    for i, city in enumerate(ind):
                        if city == dup:
                            ind[i] = missing.pop()
                            break  # 一つの重複都市を修正するごとにbreak
                return ind

            temp1 = repair(temp1)
            temp2 = repair(temp2)

            ind1[:], ind2[:] = temp1, temp2
            return ind1, ind2
        toolbox.register("mate", cxSet)
        
        # 突然変異
        def mutSet(individual):
            # 突然変異
            temp = individual[:]
            for i in range(len(temp)):
                if random.random() < MUT_PROB:
                    unused_cities = set(range(N_CITIES)) - set(temp)  # 未使用の市町村リスト
                    if not unused_cities:
                        return individual,
                    new_value = random.choice(list(unused_cities))
                    temp[i] = new_value
            individual[:] = temp
            return individual,
        toolbox.register("mutate", mutSet)


        # コスト関数
        def total_cost(individual):
            # !=はノットイコールと同意
            # 近い方の施設に輸送と仮定　　　　　　　　　　　！！！　近い方と仮定すると本来の最適化ではない？ただし、これがないと計算量が大きくなるかと思われる
            total_TC = 0
            total_IC = 0
            total_OC = 0
            TC_values = {i: 0 for i in individual}
            IC_values = {}  
            OC_values = {}  
            cities_to_facility = {i: [] for i in individual}
            
            # 施設規模
            facility_size = [0] * N_FACILITIES
            
            for city_i in range(N_CITIES):
                # TC
                # 近い方に輸送
                near_faci_distance = float('inf')
                near_faci = None
                for faci_i in individual:
                    if distance[city_i][faci_i] < near_faci_distance:
                        near_faci_distance = distance[city_i][faci_i]
                        near_faci = faci_i
                # TC = waste[city_i] * near_faci_distance * 300 / 10000
                # オーバーフロー要員（iburiの苫小牧一桁増やしたらオーバーフローしたので
                TC = float(waste[city_i]) * float(near_faci_distance) * 300 / 10000  # 明示的に float に変換
                # print(f'waste[{city_i}] = {waste[city_i]}, near_faci_distance = {near_faci_distance}, TC = {TC}, dtype of TC = {type(TC)}')
                TC_values[near_faci] += TC
                total_TC += TC
                
                facility_size[individual.index(near_faci)] += waste[city_i]
                cities_to_facility[near_faci].append(city_i)
            
            # ICとOC
            for i in range(N_FACILITIES):        
                daily_facility_size = facility_size[i]/365
                
                if daily_facility_size == 0:
                    IC_coefficient = 0
                    OC_coefficient = 0
                else:
                    if daily_facility_size >= 900:
                        IC_coefficient = float(21341 * 900** (-0.279))
                    else:
                        IC_coefficient = float(21341 * daily_facility_size** (-0.279))
                    
                    if daily_facility_size >= 600:
                        OC_coefficient = float(-5412 * np.log(600) + 36088)
                    else:
                        OC_coefficient = float(-5412 * np.log(daily_facility_size) + 36088)

                IC = IC_coefficient * daily_facility_size / 25
                total_IC += IC

                OC = OC_coefficient * facility_size[i] / 10000
                total_OC += OC

                # Update IC_values and OC_values with the facility's city index
                IC_values[individual[i]] = IC  
                OC_values[individual[i]] = OC  

            return (total_TC + total_IC + total_OC, TC_values, IC_values, OC_values, facility_size, cities_to_facility)
            
        # 評価値
        def evaluate(individual):
            if len(set(individual)) < N_FACILITIES:
                return float('inf'),
            else:
                total, _, _, _, _, _ = total_cost(individual)
                return total,

        toolbox.register("evaluate", evaluate)

        # GAループ実行
        population = toolbox.population(n=N_IND)
        hof = tools.HallOfFame(1)  # To store the best individual
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)

        algorithms.eaSimple(population, toolbox, cxpb=CX_PROB, mutpb=MUT_PROB, ngen=N_GEN, stats=stats, halloffame=hof)


        #情報表示###############################################################################################################
        best_individual = hof[0]
        output_content = []
        output_file_path = f"output_{len(best_individual)}.txt"
        
        def write_to_file(filename, content):
            filepath = os.path.join(output_directory, filename)
            with open(filepath, 'w', encoding="utf-8") as f:
                f.write(content)

        # total_costからの返り値を受け取る
        total, TC_values, IC_values, OC_values, facility_size, cities_to_facility = total_cost(best_individual)

        output_content.append("\nBest Solution:")

        # ごみ量ソート
        top_cities_indices_and_amounts = [(i, waste[i]) for i in get_top_cities(waste, top_n=TOP_N_CITIES)]
        top_cities_info = [f"{hokkaido[i]} ({amount})" for i, amount in top_cities_indices_and_amounts]
        output_content.append("ごみ量" + str(TOP_N_CITIES) + "位以内：")
        output_content.append(", ".join(top_cities_info))

        output_content.append("\n施設数: " + str(len(best_individual)))

        # 施設規模ソート
        facilities_sorted_by_size = sorted([(i, size) for i, size in enumerate(facility_size)], key=lambda x: x[1], reverse=True)
        sorted_facility_indices = [best_individual[i] for i, _ in facilities_sorted_by_size]
        for i, size in facilities_sorted_by_size:
            facility_name = hokkaido[best_individual[i]]
            city_names = ', '.join([hokkaido[city] for city in cities_to_facility[best_individual[i]]])
            output_content.append(f"{facility_name} ({size}) → receive from: {city_names}")

        # コスト
        sorted_TC = {hokkaido[key]: TC_values[key] for key in sorted_facility_indices if key in TC_values}
        sorted_IC = {hokkaido[key]: IC_values[key] for key in sorted_facility_indices if key in IC_values}
        sorted_OC = {hokkaido[key]: OC_values[key] for key in sorted_facility_indices if key in OC_values}
        output_content.append("\nTC: " + str(sorted_TC))
        output_content.append("IC: " + str(sorted_IC))
        output_content.append("OC: " + str(sorted_OC))
        output_content.append("\nTotal cost: " + str(total))

        end_time_count = time.perf_counter()
        elapsed_time_count = end_time_count - start_time_count
        output_content.append(f"\n実行時間= {round(elapsed_time_count)}秒\n\n")

        # ファイルに書き込む
        write_to_file(output_file_path, '\n'.join(output_content))
        
    sys.stdout = original_stdout
    return hof[0]
# ループ終了####################################################

best_solutions = {}

# 本チャン######################################################
for count in range(1, N_FACI_MAX + 1):
    best_individual = GA_count(count)
    best_solutions[count] = best_individual.fitness.values[0]
###############################################################

# 施設数指定####################################################
# count = 12
# best_individual = GA_count(count)
# best_solutions[count] = best_individual.fitness.values[0]
###############################################################

optimal_count = min(best_solutions, key=best_solutions.get)
original_file_name = f"output_{optimal_count}.txt"
new_file_name = f"output_{optimal_count}_best.txt"
original_file_path = os.path.join(output_directory, original_file_name)
new_file_path = os.path.join(output_directory, new_file_name)
os.rename(original_file_path, new_file_path)

print(f"最適な施設数: {optimal_count} での総コスト: {best_solutions[optimal_count]}")

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"\n実行時間= {round(elapsed_time)}秒\n\n")

