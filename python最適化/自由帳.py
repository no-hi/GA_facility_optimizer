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

toolbox = base.Toolbox()
hokkaido = data.name
waste = data.kanen
distance = data.distance
# 2次元距離リスト生成
distance = np.array(distance).reshape(len(hokkaido), len(hokkaido))


# パラメータ
N_CITIES = len(hokkaido)   # 市町村数
N_INC_MAX = 10              # 焼却施設数上限
N_TRANS_MAX = 1            # 中継施設数上限
TOP_N_CITIES = 20          #ごみ量順位下限
N_IND = 10                # 個体数
N_GEN = 10                 # 世代数
CX_PROB = 0.8              # 一様交叉
MUT_PROB = 0.3             # 突然変異
TOUR_SIZE = 4              # トーナメント
toolbox.register("select", tools.selTournament, tournsize=TOUR_SIZE)

# 最小化
creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) 
creator.create("Individual", list, fitness=creator.FitnessMin, inc_facility=None, trans_facility=None, unused_cities=None)

def get_top_cities():
    # ごみ量上位N個
    return sorted(range(len(waste)), key=lambda i: waste[i], reverse=True)[:TOP_N_CITIES]


# GA施設数ループ##################################################
def GA_count(N_INC, N_TRANS):
    optimal_stdout = sys.stdout
    with open(os.path.join(output_directory, f"output_{str(N_INC)+"&"+str(N_TRANS)}.txt"), 'a', encoding="utf-8") as f:  # 追記モードで開く
        sys.stdout = f
        start_time_count = time.perf_counter()
        print("\n------------------  処理施設数: " + str(N_INC) +"  ------------------\n")
        print("------------------  中継施設数: " + str(N_TRANS) +"  ------------------")
        print("個体数＝"+ str(N_IND))
        print("世代数＝"+ str(N_GEN))

        top_cities = get_top_cities()

        def create_individual():
            inc_facility = random.sample(top_cities, N_INC)
            trans_facility = random.sample(top_cities, N_TRANS) 
            individual = creator.Individual(inc_facility + trans_facility)
            # 処理施設の遺伝子：上位の都市からランダムに選ばれる
            individual.inc_facility = inc_facility
            # 中継施設の遺伝子：すべての都市からランダムに選ばれる
            if N_TRANS > 0:  # 中継施設が0の場合は空のリストを割り当てる
                individual.trans_facility = trans_facility
            else:
                individual.trans_facility = []
            # 未使用の都市リストを計算
            individual.unused_cities = set(range(N_CITIES)) - set(individual.inc_facility) - set(individual.trans_facility)            
            return individual       
        toolbox.register("individual", create_individual)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        def repair(individual):
            unused = individual.unused_cities
            combined = individual.inc_facility + individual.trans_facility
            
            # 重複要素を置き換える
            # 重複している要素ごとに、保持するインスタンスをランダムに選択
            facility_count = collections.Counter(combined)
            to_replace = {}
            for facility in facility_count:
                if facility_count[facility] > 1:
                    # 重複しているインデックスを全て見つける
                    indices = [i for i, x in enumerate(combined) if x == facility]
                    # 一つをランダムに選んで保持し、他は置き換え対象とする
                    keep = random.choice(indices)
                    to_replace[facility] = [idx for idx in indices if idx != keep]
            # 置き換え対象のインデックスに対して、unusedから要素を選んで置き換え
            for facility, indices in to_replace.items():
                for i in indices:
                    if unused:  # unusedが空でないことを確認
                        new_facility = random.choice(list(unused))
                        unused.remove(new_facility)
                        combined[i] = new_facility

            new_unused = list(set(range(N_CITIES)) - set(combined))

            individual.inc_facility = combined[:N_INC]
            individual.trans_facility = combined[N_INC:N_INC + N_TRANS]
            individual.unused_cities = new_unused
            individual[:] = individual.inc_facility + individual.trans_facility
            
            return individual

        def cxSet(ind1, ind2):
            # 処理施設の遺伝子リストでの一様交叉
            for i in range(len(ind1.inc_facility)):
                if random.random() < CX_PROB:
                    ind1.inc_facility[i], ind2.inc_facility[i] = ind2.inc_facility[i], ind1.inc_facility[i]
            
            # 中継施設の遺伝子リストでの一様交叉
            for i in range(len(ind1.trans_facility)):
                if random.random() < CX_PROB:
                    ind1.trans_facility[i], ind2.trans_facility[i] = ind2.trans_facility[i], ind1.trans_facility[i]

            # 個体の修正
            ind1 = repair(ind1)
            ind2 = repair(ind2)
            ind1[:] = ind1.inc_facility + ind1.trans_facility
            ind2[:] = ind2.inc_facility + ind2.trans_facility

            return ind1, ind2
        toolbox.register("mate", cxSet)

        def mutSet(individual):
            unused = list(individual.unused_cities)
            
            # 処理施設の突然変異
            for i in range(len(individual.inc_facility)):
                if random.random() < MUT_PROB:
                    if unused:
                        new_value = random.choice(unused)
                        unused.append(individual.inc_facility[i])
                        individual.inc_facility[i] = new_value
                        unused.remove(new_value)

            # 中継施設の突然変異
            for i in range(len(individual.trans_facility)):
                if random.random() < MUT_PROB:
                    if unused:
                        new_value = random.choice(unused)
                        unused.append(individual.trans_facility[i])
                        individual.trans_facility[i] = new_value
                        unused.remove(new_value)

            individual.unused_cities = set(unused)
            individual[:] = individual.inc_facility + individual.trans_facility
            
            return individual,
        toolbox.register("mutate", mutSet)

        def total_cost(individual):            
            def TC(individual):
                # 近い方の施設に輸送と仮定！！！　近い方と仮定すると本来の最適化ではない？ただし、これがないと計算量が大きくなるかと思われる
                total_TC = 0
                total_TC_direct = 0
                total_TC_indirect = 0
                TC_direct_values = {i: 0 for i in individual.inc_facility}
                TC_indirect_values = {i: 0 for i in individual.trans_facility}
                cities_to_inc = {i: [] for i in individual.inc_facility}
                cities_to_trans = {i: [] for i in individual.trans_facility}
                trans_to_inc = {inc_faci: set() for inc_faci in individual.inc_facility}   # 重複追加を防ぐためセットでつくる

                yearly_inc_size = [0] * N_INC
                yearly_trans_size = [0] * N_TRANS

                inc_faci = individual.inc_facility
                trans_faci = individual.trans_facility if N_TRANS > 0 else []
                for city_i in range(N_CITIES):
                    # 直接輸送：最も近い焼却施設へ
                    # near_~_faci_i=individual.~_facilityのリスト長さ内での施設番号
                    near_inc_faci_i = min(range(len(inc_faci)), key=lambda x: distance[city_i][inc_faci[x]])
                    near_inc_distance = distance[city_i][inc_faci[near_inc_faci_i]]
                    TC_direct = float(waste[city_i]) * near_inc_distance * 300 / 10000

                    # 中継輸送：最も近い中継施設経由で焼却施設へ
                    if N_TRANS > 0:
                        near_trans_faci_i = min(range(len(trans_faci)), key=lambda x: distance[city_i][trans_faci[x]])
                        near_trans_distance = distance[city_i][trans_faci[near_trans_faci_i]]
                        near_inc_from_trans_faci_i = min(range(len(inc_faci)), key=lambda x: distance[trans_faci[near_trans_faci_i]][inc_faci[x]])
                        near_inc_from_trans_distance = distance[trans_faci[near_trans_faci_i]][inc_faci[near_inc_from_trans_faci_i]]
                        TC_indirect = (float(waste[city_i]) * near_trans_distance * 300 + float(waste[city_i]) * near_inc_from_trans_distance * 300 * (2/8)) / 10000

                        # 最もコストが低い輸送経路を選択
                        if TC_direct <= TC_indirect:
                            # 直接輸送コストを焼却施設に加算
                            TC_direct_values[inc_faci[near_inc_faci_i]] += TC_direct
                            # 市町村から焼却施設への割り当て
                            yearly_inc_size[near_inc_faci_i] += waste[city_i]
                            total_TC_direct += TC_direct
                            total_TC += TC_direct
                            cities_to_inc[inc_faci[near_inc_faci_i]].append(city_i)

                        else:
                            # 中継輸送コストを中継施設に加算
                            TC_indirect_values[trans_faci[near_trans_faci_i]] += TC_indirect
                            # 市町村から中継施設への割り当て
                            yearly_trans_size[near_trans_faci_i] += waste[city_i]
                            # 中継施設から焼却施設への割り当て
                            yearly_inc_size[near_inc_from_trans_faci_i] += waste[city_i]
                            total_TC_indirect += TC_indirect  
                            total_TC += TC_indirect
                            cities_to_trans[trans_faci[near_trans_faci_i]].append(city_i)
                            trans_to_inc[inc_faci[near_inc_from_trans_faci_i]].add(trans_faci[near_trans_faci_i])
                
                    else:
                        # 中継施設がない場合は直接輸送のコストのみ加算
                        TC_direct_values[inc_faci[near_inc_faci_i]] += TC_direct
                        yearly_inc_size[near_inc_faci_i] += waste[city_i]
                        total_TC_direct += TC_direct
                        total_TC += TC_direct
                        cities_to_inc[inc_faci[near_inc_faci_i]].append(city_i)

                return (total_TC, TC_direct_values, TC_indirect_values, yearly_inc_size, yearly_trans_size , cities_to_inc , cities_to_trans , trans_to_inc)
            total_TC, TC_direct_values, TC_indirect_values, yearly_inc_size, yearly_trans_size , cities_to_inc , cities_to_trans , trans_to_inc = TC(individual)
            
            def ICOC(individual):
                # IC_INCとOC_INC
                total_IC_inc = 0
                total_OC_inc = 0
                total_IC_trans = 0
                total_OC_trans = 0
                IC_inc_values = {}  
                OC_inc_values = {} 
                IC_trans_values = {}  
                OC_trans_values = {}  
                for i in range(N_INC):        
                    daily_inc_size = yearly_inc_size[i]/365
                    
                    if daily_inc_size == 0:
                        IC_INC_coef = 0
                        OC_INC_coef = 0
                    else:
                        if daily_inc_size >= 900:
                            IC_INC_coef = float(21341 * 900** (-0.279))
                        else:
                            IC_INC_coef = float(21341 * daily_inc_size** (-0.279))
                        
                        if daily_inc_size >= 600:
                            OC_INC_coef = float(-5412 * np.log(600) + 36088)
                        else:
                            OC_INC_coef = float(-5412 * np.log(daily_inc_size) + 36088)

                    IC_INC = IC_INC_coef * daily_inc_size / 25
                    total_IC_inc += IC_INC

                    OC_INC = OC_INC_coef * yearly_inc_size[i] / 10000
                    total_OC_inc += OC_INC

                    # Update IC_inc_values and OC_inc_values with the facility's city index
                    IC_inc_values[individual.inc_facility[i]] = IC_INC  
                    OC_inc_values[individual.inc_facility[i]] = OC_INC
                
                return (total_IC_inc, total_OC_inc, total_IC_trans, total_OC_trans, IC_inc_values, OC_inc_values, IC_trans_values ,OC_trans_values)
            total_IC_inc, total_OC_inc, total_IC_trans, total_OC_trans, IC_inc_values, OC_inc_values, IC_trans_values ,OC_trans_values = ICOC(individual)
            
            total_cost_ = total_TC + total_IC_inc + total_OC_inc + total_IC_trans + total_OC_trans
            return (total_cost_, TC_direct_values, IC_inc_values, OC_inc_values, TC_indirect_values , IC_trans_values ,OC_trans_values , yearly_inc_size, yearly_trans_size , cities_to_inc , cities_to_trans , trans_to_inc)

        def evaluate(individual):
            if (len(set(individual.inc_facility)) + len(set(individual.trans_facility))) < N_INC + N_TRANS:
                return float('inf'),
            else:
                total_cost_, *_ = total_cost(individual)            
                return total_cost_,        
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
        output_file_path = f"output_{str(len(best_individual.inc_facility))+"&"+str(len(best_individual.trans_facility))}.txt"


        def write_to_file(filename, content):
            filepath = os.path.join(output_directory, filename)
            with open(filepath, 'w', encoding="utf-8") as f:
                f.write(content)

        # total_costからの返り値を受け取る
        total_cost_, TC_direct_values, IC_inc_values, OC_inc_values, TC_indirect_values, IC_trans_values, OC_trans_values, yearly_inc_size, yearly_trans_size, cities_to_inc, cities_to_trans, trans_to_inc = total_cost(best_individual)
        output_content = ["\nBest Solution:"]
        
        def calculate_and_format_inc_facility(facility_key, inc_size, yearly_trans_size, best_individual, cities_to_inc, trans_to_inc, hokkaido_map):
            direct_size = inc_size - sum(yearly_trans_size[best_individual.trans_facility.index(trans)] for trans in trans_to_inc[facility_key])
            city_to_inc_names = ', '.join([hokkaido_map[city] for city in cities_to_inc[facility_key]])
            formatted_output = [f"direct {hokkaido_map[facility_key]}({direct_size})/{inc_size} → receive from: {city_to_inc_names}"]

            indirect_size = sum(yearly_trans_size[best_individual.trans_facility.index(trans)] for trans in trans_to_inc[facility_key])
            if indirect_size > 0:
                trans_to_inc_names = ', '.join([hokkaido_map[trans] + "(" + str(yearly_trans_size[best_individual.trans_facility.index(trans)]) + ")" for trans in trans_to_inc[facility_key]])
                formatted_output.append(f"indirect {hokkaido_map[facility_key]}({indirect_size})/{inc_size} → receive from: {trans_to_inc_names}")

            return formatted_output

        # ごみ量ソート
        top_cities_info = [f"{hokkaido[i]} ({waste[i]})" for i in get_top_cities()]
        output_content.append("ごみ量" + str(TOP_N_CITIES) + "位以内：")
        output_content.append(", ".join(top_cities_info))

        # 焼却施設情報
        output_content.append("\n焼却施設数: " + str(len(best_individual.inc_facility)))

        # 焼却施設の詳細情報
        sorted_inc_size = sorted([(i, inc_size) for i, inc_size in enumerate(yearly_inc_size)], key=lambda x: x[1], reverse=True)
        for i, inc_size in sorted_inc_size:
            inc_key = best_individual.inc_facility[i]
            output_content.extend(calculate_and_format_inc_facility(inc_key, inc_size, yearly_trans_size, best_individual, cities_to_inc, trans_to_inc, hokkaido))

        # 中継施設情報
        output_content.append("\n中継施設数: " + str(len(best_individual.trans_facility)))

        # 中継施設のコスト関連情報
        sorted_trans_size = sorted([(i, trans_size) for i, trans_size in enumerate(yearly_trans_size)], key=lambda x: x[1], reverse=True)
        sorted_trans_i = [best_individual.trans_facility[i] for i, _ in sorted_trans_size]

        sorted_TC_indirect = {hokkaido[key]: TC_indirect_values[key] for key in sorted_trans_i if key in TC_indirect_values}
        sorted_IC_trans = {hokkaido[key]: IC_trans_values[key] for key in sorted_trans_i if key in IC_trans_values}
        sorted_OC_trans = {hokkaido[key]: OC_trans_values[key] for key in sorted_trans_i if key in OC_trans_values}
        output_content.append("\nTC_indirect: " + str(sorted_TC_indirect))
        output_content.append("IC_trans: " + str(sorted_IC_trans))
        output_content.append("OC_trans: " + str(sorted_OC_trans))

        # 総コスト
        output_content.append("\nTotal cost: " + str(total_cost_))

        # 実行時間の計算と出力
        end_time_count = time.perf_counter()
        elapsed_time_count = end_time_count - start_time_count
        output_content.append(f"\n実行時間= {round(elapsed_time_count)}秒\n\n")

        # ファイルに書き込む
        write_to_file(output_file_path, '\n'.join(output_content))


        
    sys.stdout = optimal_stdout

    return hof[0]

# ループ終了########################################################################################################################

best_solutions = {}

# 本チャン########################################################################
for count_inc in range(1, N_INC_MAX + 1):
    for count_trans in range(N_TRANS_MAX + 1):
        best_individual = GA_count(count_inc,count_trans)
        best_solutions[count_inc,count_trans] = best_individual.fitness.values[0]
#################################################################################

# 施設数指定######################################################################
# count_inc = 1
# count_trans = 0
# best_individual = GA_count(count_inc,count_trans)
# best_solutions[count_inc,count_trans] = best_individual.fitness.values[0]
#################################################################################

optimal_count_inc = min(best_solutions, key=lambda x: best_solutions[x])[0]
optimal_count_trans = min(best_solutions, key=lambda x: best_solutions[x])[1]
optimal_file_name = f"output_{str(optimal_count_inc)+"&"+str(optimal_count_trans)}.txt"
new_file_name = f"output_{str(optimal_count_inc)+"&"+str(optimal_count_trans)}_best.txt"
optimal_file_path = os.path.join(output_directory, optimal_file_name)
new_file_path = os.path.join(output_directory, new_file_name)
os.rename(optimal_file_path, new_file_path)

print(f"最適な焼却＆中継施設数: {str(optimal_count_inc)+"&"+str(optimal_count_trans)} での総コスト: {best_solutions[optimal_count_inc,optimal_count_trans]}")

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"\n実行時間= {round(elapsed_time)}秒\n\n")

