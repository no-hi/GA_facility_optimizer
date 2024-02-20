from deap import base, creator, tools, algorithms
import random
import numpy as np
import time
import sys
import collections
import math
import data
import GA_function_cost_pin.GA_input_cost as input
import GA_function_cost_pin.GA_output_display_cost as output_display
import GA_function_cost_pin.GA_local_cost as local



waste_name = input.waste_name
N_CITIES = input.N_CITIES
N_INC_INITIAL = input.N_INC_INITIAL
N_INC_MAX = input.N_INC_MAX
N_TRANS_INITIAL = input.N_TRANS_INITIAL
N_TRANS_MAX = input.N_TRANS_MAX
N_IND_UNIT = input.N_IND_UNIT
N_GEN = input.N_GEN 
CX_PROB = input.CX_PROB
MUT_PROB = input.MUT_PROB
TOUR_SIZE = input.TOUR_SIZE
ELITE_SIZE = input.ELITE_SIZE
UNIT_TRANS = input. UNIT_TRANS
UNIT_TRANS2 = input.UNIT_TRANS2
restarting_output_directory = input.restarting_output_directory
# TOP_N_CITIES = N_INC + N_TRANS +10          # ごみ量順位下限→ループ内で設定

hokkaido = data.name
distance = data.distance
distance = np.array(distance).reshape(len(hokkaido), len(hokkaido)) #2次元距離リスト生成
waste = getattr(data, waste_name)
cities_zero = [i for i in range(N_CITIES) if waste[i] == 0]


toolbox = base.Toolbox()
toolbox.register("select", tools.selTournament, tournsize=TOUR_SIZE)


# 最小化
creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) 
creator.create("Individual", list, fitness=creator.FitnessMin, inc_facility=None, trans_facility=None, unused_cities=None)

# GA施設数ループ##################################################
def GA_optimization(N_INC, N_TRANS, current_time, output_directory, lock, cost_2D, counter, lock2):
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
        # incとtransの重複があれば、trans該当部分のみ変更
        if duplicates:
            for facility in duplicates:
                indices = [i for i, x in enumerate(individual.trans_facility) if x == facility]
                for i in indices:
                    new_facility = random.choice([city for city in list(individual.unused_cities) if city not in cities_zero])
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
                        new_facility = random.choice([city for city in list(individual.unused_cities) if city not in cities_zero])
                        individual.unused_cities.remove(new_facility)
                        combined[idx] = new_facility

        individual.inc_facility = combined[:N_INC]
        individual.trans_facility = combined[N_INC:]      
        individual[:] = individual.inc_facility + individual.trans_facility
        return individual
    toolbox.register("repair", repair)
    
    # 全topでやるならunused_citiesかつtopから選ぶ
    def cxSet(ind1, ind2):
        # 正しい個体の長さに修正するための呼び出し
        def ensure_correct_length(individual, correct_length_inc, correct_length_trans):
            combined = individual.inc_facility + individual.trans_facility
            individual[:] = combined
            # 焼却施設の長さ調整
            if len(individual.inc_facility) > correct_length_inc:
                print("不正なinc_facility長さを修正:", len(individual.inc_facility), "->", correct_length_inc)
                individual.inc_facility = individual.inc_facility[:correct_length_inc]
            elif len(individual.inc_facility) < correct_length_inc:
                print("不正なinc_facility長さを修正:", len(individual.inc_facility), "->", correct_length_inc)
                while len(individual.inc_facility) < correct_length_inc:
                    new_value = random.choice([city for city in list(individual.unused_cities) if city not in cities_zero])
                    individual.inc_facility.append(new_value)
                    individual.unused_cities.remove(new_value)
            # 中継施設の長さ調整
            if len(individual.trans_facility) > correct_length_trans:
                print("不正なtrans_facility長さを修正:", len(individual.trans_facility), "->", correct_length_trans)
                individual.trans_facility = individual.trans_facility[:correct_length_trans]
            elif len(individual.trans_facility) < correct_length_trans:
                print("不正なtrans_facility長さを修正:", len(individual.trans_facility), "->", correct_length_trans)
                while len(individual.trans_facility) < correct_length_trans:
                    new_value = random.choice([city for city in list(individual.unused_cities) if city not in cities_zero])
                    individual.trans_facility.append(new_value)
                    individual.unused_cities.remove(new_value)
            # 個体全体を再構築
            individual[:] = individual.inc_facility + individual.trans_facility
            individual.unused_cities = set(range(N_CITIES)) - set(individual)
        ensure_correct_length(ind1, N_INC, N_TRANS)
        ensure_correct_length(ind2, N_INC, N_TRANS)

                
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
                new_value = random.choice([city for city in list(individual.unused_cities) if city not in cities_zero])
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
                    TC_indirect = (float(waste[city_i]) * near_trans_distance * UNIT_TRANS + float(waste[city_i]) * near_inc_from_trans_distance * UNIT_TRANS2) / 10000

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

                    IC_INC = IC_INC_coef * daily_inc_size * (153.2/94.7) / 25
                    total_IC_inc += IC_INC

                    OC_INC = OC_INC_coef * yearly_inc_size[i] * (109.9/89.78) / 10000
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
                            CAR_trans = math.ceil(daily_trans_size / 10)
                            # CT＝建設費×現在の建築資材指数/式導出時指数、CB＝車両購入費
                            C_T= float(216468*daily_trans_size**(-0.643)*1000*daily_trans_size/25) * (153.2/92.3) /10000
                            C_B = float((1+0.4)*10**7 *CAR_trans /7) /10000
                            IC_TRANS = C_T+C_B

                            # CM=整備補修費、CP=人件費、CE=電気使用料
                            C_M = float(0.02*25*C_T*10000) /10000
                            C_P = float(7*10**6 * (4 + int(3*daily_trans_size/100 - 1))) /10000
                            # 2021日本産業用平均電気価格＝19.28円/kWh
                            C_E = float(6200*19.28*daily_trans_size) /10000
                            OC_TRANS = C_M + C_P + C_E
                        
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
        # best_individualのコスト表示
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
                    TC_indirect = (float(waste[city_i]) * near_trans_distance * UNIT_TRANS + float(waste[city_i]) * near_inc_from_trans_distance * UNIT_TRANS2) / 10000

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

                    IC_INC = IC_INC_coef * daily_inc_size * (153.2/94.7) / 25
                    total_IC_inc += IC_INC

                    OC_INC = OC_INC_coef * yearly_inc_size[i] * (109.9/89.78) / 10000
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
                            CAR_trans = math.ceil(daily_trans_size / 10)
                            # CT＝建設費、CB＝車両購入費
                            C_T= float(216468*daily_trans_size**(-0.643)*1000*daily_trans_size/25) * (153.2/92.3) /10000
                            C_B = float((1+0.4)*10**7 *CAR_trans /7) /10000
                            IC_TRANS = C_T+C_B

                            # CM=整備補修費、CP=人件費、CE=電気使用料
                            C_M = float(0.02*25*C_T*10000) /10000
                            C_P = float(7*10**6 * (4 + int(3*daily_trans_size/100 - 1))) /10000
                            # 2021日本産業用平均電気価格＝19.28円/kWh
                            C_E = float(6200*19.28*daily_trans_size) /10000
                            OC_TRANS = C_M + C_P + C_E
                        
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
        if set(individual.inc_facility) & set(individual.trans_facility) or (len(set(individual.inc_facility)) + len(set(individual.trans_facility))) != N_INC + N_TRANS:
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
        
        with lock2:
            if sumgen % 10 == 0:
                sys.stdout.write(f"{N_INC}&{N_TRANS}：世代{sumgen}\n")
                sys.stdout.flush()
        
        if min_change_count >= 10*(N_INC+N_TRANS):
            break
    
    best_individual = hof[0]
    best_individual_after = local.local_optimization(best_individual, total_cost, cities_zero)
    localmark=False if best_individual.fitness.values[0] == best_individual_after.fitness.values[0] else True
    output_display.output_info(N_INC, N_TRANS, N_IND, get_top_cities, total_cost_info, gen_info, sumgen, best_individual_after, start_time_count, current_time, output_directory, lock, cost_2D, counter, localmark, lock2)

    
    return best_individual_after


