from deap import base, creator, tools, algorithms
import os
import random
import numpy as np
import time
import datetime
import collections
import data

toolbox = base.Toolbox()
hokkaido = data.name
# パラメータ##########################################################
waste_name = "sanpai"
N_CITIES = len(hokkaido)   # 市町村数
N_INC_INITIAL = 1          # 焼却初期値
N_INC_MAX = 32             # 焼却上限
N_TRANS_INITIAL = 0        # 中継初期値
N_TRANS_MAX = 12           # 中継上限
# TOP_N_CITIES = N_INC + N_TRANS +10          # ごみ量順位下限→ループ内で設定
N_IND_UNIT = 50            # 1施設当たり個体数
N_GEN = 1000               # 世代数
CX_PROB = 0.7              # 一様交叉
MUT_PROB = 0.3             # 突然変異
TOUR_SIZE = 4              # トーナメント
ELITE_SIZE = 0.1           # エリートサイズ
UNIT_TRANS = 300          # 広域輸送単価
toolbox.register("select", tools.selTournament, tournsize=TOUR_SIZE)
#####################################################################
waste = getattr(data, waste_name)
distance = data.distance
distance = np.array(distance).reshape(len(hokkaido), len(hokkaido)) #2次元距離リスト生成

start_time = time.perf_counter()
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
script_name = os.path.splitext(os.path.basename(__file__))[0]
output_directory_name = f"{UNIT_TRANS}{waste_name}_{current_time}"
current_directory = os.path.dirname(os.path.abspath(__file__))
output_directory = os.path.join(current_directory, output_directory_name)
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# 最小化
creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) 
creator.create("Individual", list, fitness=creator.FitnessMin, inc_facility=None, trans_facility=None, unused_cities=None)


# GA施設数ループ##################################################
def GA_count(N_INC, N_TRANS):
    start_time_count = time.perf_counter()
    N_IND = N_IND_UNIT * (N_INC+N_TRANS)

    def get_top_cities():
        # ごみ量上位N個
        TOP_N_CITIES = N_INC + N_TRANS +10          # ごみ量順位下限
        return sorted(range(len(waste)), key=lambda i: waste[i], reverse=True)[:TOP_N_CITIES]
    top_cities = get_top_cities()

    #（TOP_N_CITIES）が（N_INC）を超える場合にエラー
    def create_individual():
        inc_facility = random.sample(top_cities, N_INC)
        trans_facility = random.sample([city for city in top_cities if city not in inc_facility], N_TRANS)
        individual = creator.Individual(inc_facility + trans_facility)
        individual.inc_facility = inc_facility
        individual.trans_facility = trans_facility if N_TRANS > 0 else []
        individual.unused_cities = set(range(N_CITIES)) - set(individual.inc_facility) - set(individual.trans_facility)
        return individual

    toolbox.register("individual", create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def repair(individual):
        duplicates = set(individual.inc_facility) & set(individual.trans_facility)
        if duplicates:
            for facility in duplicates:
                indices = [i for i, x in enumerate(individual.trans_facility) if x == facility]
                for i in indices:
                    new_facility = random.choice(list(individual.unused_cities))
                    individual.unused_cities.remove(new_facility)
                    individual.trans_facility[i] = new_facility

        combined = individual.inc_facility + individual.trans_facility
        facility_count = collections.Counter(combined)
        for facility, count in facility_count.items():
            if count > 1:
                indices = [i for i, x in enumerate(combined) if x == facility]
                keep = random.choice(indices)
                for idx in indices:
                    if idx != keep:
                        new_facility = random.choice(list(individual.unused_cities))
                        individual.unused_cities.remove(new_facility)
                        combined[idx] = new_facility

        individual.inc_facility = combined[:N_INC]
        individual.trans_facility = combined[N_INC:]      
        individual[:] = individual.inc_facility + individual.trans_facility
        return individual
    toolbox.register("repair", repair)
    
    # 全topでやるならunused_citiesかつtopから選ぶ
    def cxSet(ind1, ind2):
        # 処理施設の遺伝子リストでの一様交叉
        common_inc = set(ind1.inc_facility) & set(ind2.inc_facility)
        unique_inc1 = [gene for gene in ind1.inc_facility if gene not in common_inc]
        unique_inc2 = [gene for gene in ind2.inc_facility if gene not in common_inc]
        random.shuffle(unique_inc1)
        random.shuffle(unique_inc2)

        for i in range(len(unique_inc1)):
            if random.random() < CX_PROB:
                unique_inc1[i], unique_inc2[i] = unique_inc2[i], unique_inc1[i]

        ind1.inc_facility = sorted(list(common_inc) + unique_inc1)
        ind2.inc_facility = sorted(list(common_inc) + unique_inc2)

        # 中継施設の遺伝子リストでの一様交叉
        common_trans = set(ind1.trans_facility) & set(ind2.trans_facility)
        unique_trans1 = [gene for gene in ind1.trans_facility if gene not in common_trans]
        unique_trans2 = [gene for gene in ind2.trans_facility if gene not in common_trans]
        random.shuffle(unique_trans1)
        random.shuffle(unique_trans2)

        for i in range(len(unique_trans1)):
            if random.random() < CX_PROB:
                unique_trans1[i], unique_trans2[i] = unique_trans2[i], unique_trans1[i]

        ind1.trans_facility = sorted(list(common_trans) + unique_trans1)
        ind2.trans_facility = sorted(list(common_trans) + unique_trans2)

        ind1[:] = ind1.inc_facility + ind1.trans_facility
        ind2[:] = ind2.inc_facility + ind2.trans_facility
        ind1.unused_cities = set(range(N_CITIES)) - set(ind1)
        ind2.unused_cities = set(range(N_CITIES)) - set(ind2)

        return ind1, ind2
    toolbox.register("mate", cxSet)

    # 全topでやるならunused_citiesかつtopから選ぶ
    def mutSet(individual):
        for i in range(len(individual)):
            if random.random() < MUT_PROB:
                new_value = random.choice(list(individual.unused_cities))
                individual.unused_cities.add(individual[i])
                individual[i] = new_value
                individual.unused_cities.remove(new_value)

        individual.inc_facility = individual[:N_INC]
        individual.trans_facility = individual[N_INC:]

        return individual,
    toolbox.register("mutate", mutSet)

    def total_cost(individual):            
        def TC(individual):
            # 近い方の施設に輸送と仮定！！！　近い方と仮定すると本来の最適化ではない？ただし、これがないと計算量が大きくなるかと思われる
            total_TC = total_TC_direct = total_TC_indirect = 0
            yearly_inc_size = [0] * N_INC
            yearly_trans_size = [0] * N_TRANS
            inc_faci = individual.inc_facility
            trans_faci = individual.trans_facility if N_TRANS > 0 else []
            
            for city_i in range(N_CITIES):
                # 直接輸送：最も近い焼却施設へ
                # near_~_faci_i=individual.~_facilityのリスト長さ内での施設番号
                near_inc_faci_i = min(range(len(inc_faci)), key=lambda x: distance[city_i][inc_faci[x]])
                near_inc_distance = distance[city_i][inc_faci[near_inc_faci_i]]
                TC_direct = float(waste[city_i]) * near_inc_distance * UNIT_TRANS / 10000

                # 中継輸送：最も近い中継施設経由で焼却施設へ
                if N_TRANS > 0:
                    near_trans_faci_i = min(range(len(trans_faci)), key=lambda x: distance[city_i][trans_faci[x]])
                    near_trans_distance = distance[city_i][trans_faci[near_trans_faci_i]]
                    near_inc_from_trans_faci_i = min(range(len(inc_faci)), key=lambda x: distance[trans_faci[near_trans_faci_i]][inc_faci[x]])
                    near_inc_from_trans_distance = distance[trans_faci[near_trans_faci_i]][inc_faci[near_inc_from_trans_faci_i]]
                    TC_indirect = (float(waste[city_i]) * near_trans_distance * UNIT_TRANS + float(waste[city_i]) * near_inc_from_trans_distance * UNIT_TRANS * (2/10)) / 10000

                    # 最もコストが低い輸送経路を選択
                    if TC_direct <= TC_indirect:
                        # 直接輸送コストを焼却施設に加算
                        yearly_inc_size[near_inc_faci_i] += waste[city_i]
                        total_TC_direct += TC_direct
                        total_TC += TC_direct

                    else:
                        # 市町村から中継施設への割り当て
                        yearly_trans_size[near_trans_faci_i] += waste[city_i]
                        # 中継施設から焼却施設への割り当て
                        yearly_inc_size[near_inc_from_trans_faci_i] += waste[city_i]
                        total_TC_indirect += TC_indirect  
                        total_TC += TC_indirect
            
                else:
                    # 中継施設がない場合は直接輸送のコストのみ加算
                    yearly_inc_size[near_inc_faci_i] += waste[city_i]
                    total_TC_direct += TC_direct
                    total_TC += TC_direct

            return (total_TC, yearly_inc_size, yearly_trans_size)
        total_TC, yearly_inc_size, yearly_trans_size = TC(individual)
        
        def ICOC(individual):
            def ICOC_INC(individual):
                total_IC_inc = 0
                total_OC_inc = 0
                
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
                
                return (total_IC_inc, total_OC_inc)
            total_IC_inc, total_OC_inc = ICOC_INC(individual)

            def ICOC_TRANS(individual):
                total_IC_trans = 0
                total_OC_trans = 0
                
                if N_TRANS > 0:
                    for i in range(N_TRANS):        
                        daily_trans_size = yearly_trans_size[i]/365
                    
                        if  daily_trans_size == 0:
                            IC_TRANS = 0
                            OC_TRANS = 0
                        
                        else:
                            CAR_trans = daily_trans_size / 10
                            # CT＝建設費、CB＝車両購入費
                            C_T = float(3*10**8 * (daily_trans_size / 100)**0.7 /20) /10000
                            C_B = float((1+0.4)*10**7 *CAR_trans /7) /10000
                            IC_TRANS = C_T+C_B
                            
                            # CM=整備補修費、CP=人件費、CE=電気使用料、CW=水道費
                            C_M = float(1.344*10**6 * CAR_trans +0.4*C_T) /10000
                            C_P = float(7*10**6 * (4 + int(1.16*CAR_trans) + int(3*daily_trans_size - 1))) /10000
                            # 2021日本産業用平均電気価格＝19.28円/kWh
                            C_E = float(6200*19.28*daily_trans_size) /10000
                            # 水道代=300円/m3（松藤中継資料のエクセルの通り）
                            C_W = float(93*300*CAR_trans) /10000
                            OC_TRANS = C_M + C_P + C_E + C_W
                        
                        total_IC_trans += IC_TRANS
                        total_OC_trans += OC_TRANS
                
                return (total_IC_trans, total_OC_trans)
            if N_TRANS > 0:
                total_IC_trans, total_OC_trans = ICOC_TRANS(individual)
            else:
                total_IC_trans = total_OC_trans = 0

            return (total_IC_inc, total_OC_inc, total_IC_trans, total_OC_trans)
        total_IC_inc, total_OC_inc, total_IC_trans, total_OC_trans = ICOC(individual)
        
        total_cost_ = total_TC + total_IC_inc + total_OC_inc + total_IC_trans + total_OC_trans
        return (total_cost_, yearly_inc_size, yearly_trans_size)

    def total_cost_info(best_individual):     
        # best_individualは判明しているので、逆順で表示だけつくればよい
        def TC(best_individual):
            # 近い方の施設に輸送と仮定！！！　近い方と仮定すると本来の最適化ではない？ただし、これがないと計算量が大きくなるかと思われる
            total_TC = 0
            total_TC_direct = 0
            total_TC_indirect = 0
            TC_direct_values = {i: 0 for i in best_individual.inc_facility}
            TC_indirect_values = {i: 0 for i in best_individual.trans_facility}
            cities_to_inc = {i: [] for i in best_individual.inc_facility}
            cities_to_trans = {i: [] for i in best_individual.trans_facility}
            trans_to_inc = {inc_faci: set() for inc_faci in best_individual.inc_facility}   # 重複追加を防ぐためセットでつくる

            yearly_inc_size = [0] * N_INC
            yearly_trans_size = [0] * N_TRANS

            inc_faci = best_individual.inc_facility
            trans_faci = best_individual.trans_facility if N_TRANS > 0 else []
            for city_i in range(N_CITIES):
                # 直接輸送：最も近い焼却施設へ
                # near_~_faci_i=best_individual.~_facilityのリスト長さ内での施設番号
                near_inc_faci_i = min(range(len(inc_faci)), key=lambda x: distance[city_i][inc_faci[x]])
                near_inc_distance = distance[city_i][inc_faci[near_inc_faci_i]]
                TC_direct = float(waste[city_i]) * near_inc_distance * UNIT_TRANS / 10000

                # 中継輸送：最も近い中継施設経由で焼却施設へ
                if N_TRANS > 0:
                    near_trans_faci_i = min(range(len(trans_faci)), key=lambda x: distance[city_i][trans_faci[x]])
                    near_trans_distance = distance[city_i][trans_faci[near_trans_faci_i]]
                    near_inc_from_trans_faci_i = min(range(len(inc_faci)), key=lambda x: distance[trans_faci[near_trans_faci_i]][inc_faci[x]])
                    near_inc_from_trans_distance = distance[trans_faci[near_trans_faci_i]][inc_faci[near_inc_from_trans_faci_i]]
                    TC_indirect = (float(waste[city_i]) * near_trans_distance * UNIT_TRANS + float(waste[city_i]) * near_inc_from_trans_distance * UNIT_TRANS * (2/10)) / 10000

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

            return (total_TC, total_TC_direct, total_TC_indirect, TC_direct_values, TC_indirect_values, yearly_inc_size, yearly_trans_size , cities_to_inc , cities_to_trans , trans_to_inc)
        total_TC, total_TC_direct, total_TC_indirect, TC_direct_values, TC_indirect_values, yearly_inc_size, yearly_trans_size , cities_to_inc , cities_to_trans , trans_to_inc = TC(best_individual)
        
        def ICOC(best_individual):
            def ICOC_INC(best_individual):
                # IC_INCとOC_INC
                total_IC_inc = 0
                total_OC_inc = 0
                IC_inc_values = {}  
                OC_inc_values = {} 
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
                    IC_inc_values[best_individual.inc_facility[i]] = IC_INC
                    OC_inc_values[best_individual.inc_facility[i]] = OC_INC
                
                return (total_IC_inc, total_OC_inc, IC_inc_values, OC_inc_values)
            total_IC_inc, total_OC_inc, IC_inc_values, OC_inc_values = ICOC_INC(best_individual)

            def ICOC_TRANS(best_individual):
                # IC_TRANSとOC_TRANS
                total_IC_trans = 0
                total_OC_trans = 0
                IC_trans_values = {}  
                OC_trans_values = {}
                if N_TRANS > 0:
                    for i in range(N_TRANS):        
                        daily_trans_size = yearly_trans_size[i]/365
                    
                        if  daily_trans_size == 0:
                            IC_TRANS = 0
                            OC_TRANS = 0
                        
                        else:
                            CAR_trans = daily_trans_size / 10
                            # CT＝建設費、CB＝車両購入費
                            C_T = float(3*10**8 * (daily_trans_size / 100)**0.7 /20) /10000
                            C_B = float((1+0.4)*10**7 *CAR_trans /7) /10000
                            IC_TRANS = C_T+C_B
                            
                            # CM=整備補修費、CP=人件費、CE=電気使用料、CW=水道費
                            C_M = float(1.344*10**6 * CAR_trans +0.4*C_T) /10000
                            C_P = float(7*10**6 * (4 + int(1.16*CAR_trans) + int(3*daily_trans_size - 1))) /10000
                            # 2021日本産業用平均電気価格＝19.28円/kWh
                            C_E = float(6200*19.28*daily_trans_size) /10000
                            # 水道代=300円/m3（松藤中継資料のエクセルの通り）
                            C_W = float(93*300*CAR_trans) /10000
                            OC_TRANS = C_M + C_P + C_E + C_W
                        
                        total_IC_trans += IC_TRANS
                        total_OC_trans += OC_TRANS
                        
                        IC_trans_values[best_individual.trans_facility[i]] = IC_TRANS  
                        OC_trans_values[best_individual.trans_facility[i]] = OC_TRANS
                
                return (total_IC_trans, total_OC_trans, IC_trans_values ,OC_trans_values)
            total_IC_trans, total_OC_trans, IC_trans_values ,OC_trans_values = ICOC_TRANS(best_individual)

            return (total_IC_inc, total_OC_inc, total_IC_trans, total_OC_trans, IC_inc_values, OC_inc_values, IC_trans_values ,OC_trans_values)
        total_IC_inc, total_OC_inc, total_IC_trans, total_OC_trans, IC_inc_values, OC_inc_values, IC_trans_values ,OC_trans_values = ICOC(best_individual)
        
        total_cost_ = total_TC + total_IC_inc + total_OC_inc + total_IC_trans + total_OC_trans
        return (total_cost_, total_TC_direct, total_TC_indirect, total_IC_inc, total_OC_inc, total_IC_trans, total_OC_trans, TC_direct_values, IC_inc_values, OC_inc_values, TC_indirect_values , IC_trans_values ,OC_trans_values , yearly_inc_size, yearly_trans_size , cities_to_inc , cities_to_trans , trans_to_inc)

    def evaluate(individual):
        if (len(set(individual.inc_facility)) + len(set(individual.trans_facility))) != N_INC + N_TRANS:
            return float('inf'),
        else:
            total_cost_, *_ = total_cost(individual)            
            return total_cost_,        
    toolbox.register("evaluate", evaluate)


    population = toolbox.population(n=N_IND)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("max", np.max)
    stats.register("min", np.min)
    
    # エリートサイズを設定（個体数の10%）
    elite_size = int(ELITE_SIZE * len(population))
    def elitism(population, elite_size):
        sorted_population = sorted(population, key=lambda ind: ind.fitness.values)
        return sorted_population[:elite_size]

    # GAループ
    prev_min = float('inf')
    min_change_count = 0    
    sumgen = 0
    gen_info = []
    for gen in range(N_GEN):
        sumgen = gen + 1
        for individual in population:
            if len(set(individual)) < N_INC + N_TRANS :
                individual = toolbox.repair(individual)
        # 次世代の個体を生成
        offspring = algorithms.varAnd(population, toolbox, cxpb=CX_PROB, mutpb=MUT_PROB)
        population[:] = toolbox.select(offspring, len(population) - elite_size)
        # エリート個体を選定
        elites = elitism(population, elite_size)        
        # 次世代の個体を生成（エリート個体は除外して生成）
        population.extend(elites)
        
        # 新たに評価する個体をカウント
        neval = sum(1 for ind in offspring if not ind.fitness.valid)

        # 個体を評価
        fitnesses = map(toolbox.evaluate, offspring)
        for fit, ind in zip(fitnesses, offspring):
            ind.fitness.values = fit
        population = toolbox.select(offspring, len(population))
        hof.update(population)
        record = stats.compile(population)

        # 最小値の変化をチェック
        current_min = record['min']
        if current_min == prev_min:
            min_change_count += 1
        else:
            prev_min = current_min
            min_change_count = 0

        gen_info.append(f"{gen}: neval={neval}{record} best={hof[0].fitness.values[0]}")
        print(f"（{waste_name}{UNIT_TRANS}）焼却{N_INC}：中継{N_TRANS} → 世代{sumgen}")
        
        # 最小値が一定世代変化しない場合、ループを抜ける
        # if best_in_generation_count >= 20*(1+(N_INC+N_TRANS)//3):
        if min_change_count >= 10*(N_INC+N_TRANS):
            break
    
    #情報表示###############################################################################################################
    best_individual = hof[0]
    output_content = []
    output_file_path = f"{waste_name}_{len(best_individual.inc_facility)}&{len(best_individual.trans_facility)}.txt"
    
    # total_costからの返り値を受け取る
    total_cost_, total_TC_direct, total_TC_indirect, total_IC_inc, total_OC_inc, total_IC_trans, total_OC_trans, TC_direct_values, IC_inc_values, OC_inc_values, TC_indirect_values , IC_trans_values ,OC_trans_values , yearly_inc_size, yearly_trans_size , cities_to_inc , cities_to_trans , trans_to_inc = total_cost_info(best_individual)

    def write_to_file(filename, content):
            filepath = os.path.join(output_directory, filename)
            with open(filepath, 'w', encoding="utf-8") as f:
                f.write(content)

    # 実行時間の計算と出力
    end_time_count = time.perf_counter()
    elapsed_time_count = end_time_count - start_time_count
    output_content = []
    
    # 諸情報
    output_content += ["----------------------  実行情報  ----------------------",
                    f"実行時間＝{round(elapsed_time_count)}秒",
                    f"個体数＝{str(N_IND)}",
                    f"合計世代数＝{str(sumgen)}"
                    ]
    
    # 前提情報
    top_cities_info = [f"{hokkaido[i]} ({waste[i]})" for i in get_top_cities()]
    output_content += ["------------------------  前提  ------------------------\n",
                    f"waste={waste_name}\n",
                    # f"ごみ量{str(TOP_N_CITIES)}位以内：",
                    f"ごみ量{str(len(best_individual)+10)}位以内：",                    
                    ", ".join(top_cities_info),
                    f"\n焼却施設数: {str(len(best_individual.inc_facility))}",
                    f"中継施設数: {str(len(best_individual.trans_facility))}\n",
                    f"輸送単価＝ {str(UNIT_TRANS)} 円/t/km",
                    ]
    
    # GAPlot入力情報
    def city_2d_lists(cities_to_inc, cities_to_trans):
        direct_cities_list = []
        indirect_cities_list = []

        for facility_key in cities_to_inc:
            direct_cities = [hokkaido[city] for city in cities_to_inc[facility_key]]
            direct_cities_list.append(direct_cities)

        for facility_key in cities_to_trans:
            indirect_cities = [hokkaido[city] for city in cities_to_trans[facility_key]]
            indirect_cities_list.append(indirect_cities) 
                
        return direct_cities_list, indirect_cities_list
    direct_cities_list, indirect_cities_list = city_2d_lists(cities_to_inc, cities_to_trans)
    
    sorted_inc_indices = sorted(range(len(yearly_inc_size)), key=lambda i: yearly_inc_size[i], reverse=True)
    sorted_trans_indices = sorted(range(len(yearly_trans_size)), key=lambda i: yearly_trans_size[i], reverse=True)
    inc_facility = [hokkaido[best_individual.inc_facility[inc_index]] for inc_index in sorted_inc_indices]
    
    output_content += [f"--------------------  GAPlot_input  --------------------\n",
                    f"waste ={waste_name}\n" ,
                    f"inc_size= {str([round(yearly_inc_size[i]) for i in sorted_inc_indices])}\n" ,
                    f"inc_facility = {inc_facility}",
                    f"inc_blocks = {str(direct_cities_list)}\n"  
                    ]
    
    if yearly_trans_size != []:
        trans_facility = [hokkaido[best_individual.trans_facility[trans_index]] for trans_index in sorted_trans_indices]
        output_content += [f"trans_size={str([round(yearly_trans_size[i]) for i in sorted_trans_indices])}",
                        f"trans_facility = {trans_facility}",
                        f"trans_blocks = {str(indirect_cities_list)}"
                        ]
        arrows = []
        for inc_facility_index in best_individual.inc_facility:
            trans_indices = trans_to_inc.get(inc_facility_index)

            if trans_indices:
                inc_facility_name = [hokkaido[inc_facility_index]]
                trans_facility_names = [hokkaido[trans_index] for trans_index in trans_indices]
                arrows.append([inc_facility_name, trans_facility_names])

        output_content += [f"\narrows = {arrows}\n"]
        
    else:
        output_content += [f"trans_size = []",
                        f"trans_facility = []",
                        f"trans_blocks = []",
                        f"\narrows = []\n"
                        ]
    
    # コスト情報
    sorted_inc_size = sorted(((i, inc_size) for i, inc_size in enumerate(yearly_inc_size)), key=lambda x: x[1], reverse=True)
    sorted_inc_i = [best_individual.inc_facility[i] for i, _ in sorted_inc_size]
    sorted_trans_size = sorted(((i, trans_size) for i, trans_size in enumerate(yearly_trans_size)), key=lambda x: x[1], reverse=True)
    sorted_trans_i = [best_individual.trans_facility[i] for i, _ in sorted_trans_size]

    output_content += ["\n---------------------  コスト情報  ---------------------\n",                        
                    "TC_direct: " + str({hokkaido[key]: TC_direct_values[key] for key in sorted_inc_i if key in TC_direct_values}),
                    "IC_inc: " + str({hokkaido[key]: IC_inc_values[key] for key in sorted_inc_i if key in IC_inc_values}),
                    "OC_inc: " + str({hokkaido[key]: OC_inc_values[key] for key in sorted_inc_i if key in OC_inc_values}),
                    "\nTC_indirect: " + str({hokkaido[key]: TC_indirect_values[key] for key in sorted_trans_i if key in TC_indirect_values}),
                    "IC_trans: " + str({hokkaido[key]: IC_trans_values[key] for key in sorted_trans_i if key in IC_trans_values}),
                    "OC_trans: " + str({hokkaido[key]: OC_trans_values[key] for key in sorted_trans_i if key in OC_trans_values}) + "\n",
                    "="*len(str("Total cost: ") + str(total_cost_)),
                    "Total cost: " + str(total_cost_),
                    "="*len(str("Total cost: ") + str(total_cost_))
                    ]
    
    # 輸送情報
    output_content += ["\n----------------------  輸送情報  ----------------------\n"]
    def format_faci(facility_key, yearly_inc_size, yearly_trans_size, best_individual, cities_to_inc, trans_to_inc):
        direct_size = yearly_inc_size - sum(yearly_trans_size[best_individual.trans_facility.index(trans)] for trans in trans_to_inc[facility_key])
        city_to_inc_names = ', '.join(hokkaido[city] for city in cities_to_inc[facility_key])
        formatted_output = [f"direct {hokkaido[facility_key]}({round(direct_size/365)}/{round(yearly_inc_size/365)}) t/day → receive from: {city_to_inc_names}"]
        
        indirect_size = sum(yearly_trans_size[best_individual.trans_facility.index(trans)] for trans in trans_to_inc[facility_key])
        if indirect_size > 0:
            trans_to_inc_details = []
            for trans in trans_to_inc[facility_key]:
                cities_to_trans_names = ', '.join(hokkaido[city] for city in cities_to_trans[trans])
                trans_to_inc_details.append(f"{hokkaido[trans]}({yearly_trans_size[best_individual.trans_facility.index(trans)]}) → receive from: {cities_to_trans_names}")

            trans_to_inc_details_str = '\n                                                    　　　'.join(trans_to_inc_details)
            formatted_output.append(f"indirect {hokkaido[facility_key]}({round(indirect_size/365)}/{round(yearly_inc_size/365)}) t/day → receive from: 中継施設＝ {trans_to_inc_details_str}")

        return formatted_output
    output_content.extend(item for sublist in (format_faci(best_individual.inc_facility[i], yearly_inc_size, yearly_trans_size, best_individual, cities_to_inc, trans_to_inc) for i, yearly_inc_size in sorted_inc_size) for item in sublist)
    
    # 遺伝情報    
    output_content +=["\n----------------------  遺伝情報  ----------------------\n",
                    "個体数＝"+ str(N_IND),
                    "世代数＝"+ str(N_GEN),
                    ]
    output_content += gen_info
    
    # ファイルに書き込む
    write_to_file(output_file_path, '\n'.join(output_content))
    
    
    # 折れ線グラフ用出力
    global cost_2D
    if N_INC == N_INC_INITIAL and N_TRANS == N_TRANS_INITIAL:
        cost_2D = [[] for _ in range(N_TRANS_MAX + 1)]

    cost_list = [total_TC_direct, total_TC_indirect, total_IC_inc, total_OC_inc, total_IC_trans, total_OC_trans]
    cost_2D[N_TRANS].append(cost_list)

    if N_TRANS==N_TRANS_MAX:
        with open(os.path.join(output_directory, f"GAGraph({UNIT_TRANS}{waste_name}){current_time}.txt"), 'w', encoding="utf-8") as file:
            file.write(f"inc({N_INC_INITIAL}~{N_INC})+trans({N_TRANS_INITIAL}~{N_TRANS})コスト行列\n")
            file.write(f"cost = {str(cost_2D)}\n")


    return hof[0]

# ループ終了########################################################################################################################

best_solutions = {}

# 本チャン########################################################################
for count_inc in range(N_INC_INITIAL, N_INC_MAX + 1):
    for count_trans in range(N_TRANS_INITIAL, N_TRANS_MAX + 1):
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
optimal_file_name = f"{waste_name}_{optimal_count_inc}&{optimal_count_trans}.txt"
new_file_name = f"{waste_name}_{optimal_count_inc}&{optimal_count_trans}_best.txt"
optimal_file_path = os.path.join(output_directory, optimal_file_name)
new_file_path = os.path.join(output_directory, new_file_name)
os.rename(optimal_file_path, new_file_path)

print(f"最適な焼却＆中継施設数: {optimal_count_inc}&{optimal_count_trans} での総コスト: {best_solutions[optimal_count_inc,optimal_count_trans]}")

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"\n実行時間= {round(elapsed_time/3600)}h\n\n")

