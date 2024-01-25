from deap import base, creator, tools, algorithms
import os
import random
import numpy as np
import time
import datetime
import collections
import multiprocessing
import sys
import data
import subprocess
import GA中継_input as input
import smtplib
import traceback
from email.mime.text import MIMEText

add_name = input.add_name
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
toolbox = base.Toolbox()
toolbox.register("select", tools.selTournament, tournsize=TOUR_SIZE)


# 最小化
creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) 
creator.create("Individual", list, fitness=creator.FitnessMin, inc_facility=None, trans_facility=None, unused_cities=None)

# GA施設数ループ##################################################
def GA_optimization(N_INC, N_TRANS, output_directory, current_time, lock, cost_2D, counter):
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
                            CAR_trans = round(daily_trans_size / 10)
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
                            CAR_trans = round(daily_trans_size / 10)
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
        
        if min_change_count >= 10*(N_INC+N_TRANS):
            break
    
    #情報表示###############################################################################################################
    best_individual = hof[0]
    output_content = []
    output_file_path = f"{waste_name}_{len(best_individual.inc_facility)}&{len(best_individual.trans_facility)}.txt"
    
    # total_costからの返り値を受け取る
    total_cost_, total_TC_direct, total_TC_indirect, total_IC_inc, total_OC_inc, total_IC_trans, total_OC_trans, TC_direct_values, IC_inc_values, OC_inc_values, TC_indirect_values , IC_trans_values ,OC_trans_values , yearly_inc_size, yearly_trans_size , cities_to_inc , cities_to_trans , trans_to_inc = total_cost_info(best_individual)
    cost_list = [total_TC_direct, total_TC_indirect, total_IC_inc, total_OC_inc, total_IC_trans, total_OC_trans]

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
                    f"合計世代数＝{str(sumgen)}",
                    "="*len(str("Total cost: ") + str(total_cost_)),
                    "Total cost: " + str(total_cost_),
                    "="*len(str("Total cost: ") + str(total_cost_)),
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

    output_content += ["\n---------------------  コスト情報  ---------------------",
                    str(cost_list)+ "\n",
                    "TC_direct: " + str({hokkaido[key]: TC_direct_values[key] for key in sorted_inc_i if key in TC_direct_values}),
                    "IC_inc: " + str({hokkaido[key]: IC_inc_values[key] for key in sorted_inc_i if key in IC_inc_values}),
                    "OC_inc: " + str({hokkaido[key]: OC_inc_values[key] for key in sorted_inc_i if key in OC_inc_values}),
                    "\nTC_indirect: " + str({hokkaido[key]: TC_indirect_values[key] for key in sorted_trans_i if key in TC_indirect_values}),
                    "IC_trans: " + str({hokkaido[key]: IC_trans_values[key] for key in sorted_trans_i if key in IC_trans_values}),
                    "OC_trans: " + str({hokkaido[key]: OC_trans_values[key] for key in sorted_trans_i if key in OC_trans_values}) + "\n"
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

            trans_to_inc_details_str = '\n'.join(trans_to_inc_details)
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
    
    
    # GA_Graph用出力
    def extract_list(shared_list):  # 共有化されたcost_2Dを通常リストに変換
        if isinstance(shared_list, multiprocessing.managers.ListProxy):
            return [extract_list(item) for item in shared_list]
        else:
            return shared_list
    
    with lock: # 共有化されたcost2Dやcounterをいじるときはlockをかける
        cost_2D[N_INC-N_INC_INITIAL][N_TRANS-N_TRANS_INITIAL] = cost_list
        counter[N_INC] += 1        
        all_conditions_met = False
        if counter[N_INC] == N_TRANS_MAX - N_TRANS_INITIAL + 1:
            normal_cost_2D = extract_list(cost_2D)
            # 時点N_INC以下のデータのみを抽出
            filtered_cost_2D = normal_cost_2D[:N_INC]
            with open(os.path.join(output_directory, f"GA_Graph({UNIT_TRANS}{waste_name}){current_time}.txt"), 'w', encoding="utf-8") as file:
                max_filled_N_INC = max(i for i in range(N_INC_INITIAL, N_INC_MAX + 1) if all(counter[j] == N_TRANS_MAX - N_TRANS_INITIAL + 1 for j in range(N_INC_INITIAL, i + 1)))
                file.write(f"inc[{N_INC_INITIAL}~{max_filled_N_INC}]&trans[{N_TRANS_INITIAL}~{N_TRANS_MAX}]\n")
                file.write(f'foldername = "{str(waste_name)}{str(UNIT_TRANS)}"\n')
                file.write(f"cost = {str(filtered_cost_2D)}\n")
            # 自動git pull/push
            all_conditions_met = all(counter[i] == N_TRANS_MAX - N_TRANS_INITIAL + 1 for i in range(N_INC_INITIAL, N_INC + 1))
            if all_conditions_met:
                subprocess.run(["git", "pull"], check=False)
                subprocess.run(["git", "add", "."], check=False)
                subprocess.run(["git", "commit", "-m", f"自動コミット（every_INC）:{UNIT_TRANS}{waste_name}{N_INC_INITIAL}~{N_INC}&{N_TRANS_INITIAL}~{N_TRANS_MAX}"], check=False)
                subprocess.run(["git", "push"], check=False)
        
        # 並列実行用の表示
        group_size = 3  # 一行に表示する進捗表示の数
        if not all_conditions_met:
            sys.stdout.write("\033[F" * (len(cost_2D) // group_size + (len(cost_2D) % group_size > 0) + 1))
        for i in range(0, len(cost_2D), group_size):
            line_output = []
            for j in range(group_size):
                if i + j < len(cost_2D):
                    finish = cost_2D[i + j]
                    display_inc = i + j + N_INC_INITIAL
                    all_done = all(finish)  # すべてのトランザクションが完了しているかチェック
                    progress = [str(k + N_TRANS_INITIAL) if finish[k] else "@" for k in range(N_TRANS_MAX - N_TRANS_INITIAL + 1)]
                    display = ",".join(progress)
                    completion_status = "完" if all_done else "  "  # "完"またはスペースを選択
                    line_part = f"焼却{display_inc:2} → [{display}]{completion_status}"
                    line_output.append(line_part)
            sys.stdout.write("  ".join(line_output) + "\n")  # スペースを1つに縮小
        sys.stdout.write(waste_name + "\n")
        sys.stdout.flush()
    
    
    return hof[0]


# 並列実行########################################################################
def multi_task(task, output_directory, current_time, lock, cost_2D, counter):
    count_inc, count_trans = task
    best_individual = GA_optimization(count_inc, count_trans, output_directory, current_time, lock, cost_2D, counter)
    return count_inc, count_trans, best_individual.fitness.values[0]


def send_error_email(error_message):
    smtp_host = 'smtp.gmail.com' # SMTPサーバのホスト名
    smtp_port = 587 # SMTPサーバのポート番号安全接続＝587
    from_email = 'errorman15.3318@gmail.com' # 送信元のEmailアドレス
    to_email = 'hyo15.3318@gmail.com' # 送信先のEmailアドレス
    username = 'errorman15.3318@gmail.com' # SMTPサーバのユーザ名
    password = 'yurq vewc ezvo uarq' # SMTPサーバのパスワード

    msg = MIMEText(error_message)
    msg['Subject'] = 'エラーマンだよ'
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()  # TLSセキュリティを開始
        server.login(username, password)  # SMTPサーバにログイン
        server.send_message(msg)  # メールを送信

def send_end_email(end_message):
    smtp_host = 'smtp.gmail.com' # SMTPサーバのホスト名
    smtp_port = 587 # SMTPサーバのポート番号安全接続＝587
    from_email = 'enderman15.3318@gmail.com' # 送信元のEmailアドレス
    to_email = 'hyo15.3318@gmail.com' # 送信先のEmailアドレス
    username = 'enderman15.3318@gmail.com' # SMTPサーバのユーザ名
    password = 'chdw cspd yjbj avmy' # SMTPサーバのパスワード

    end_message = '\n'.join(end_message) if isinstance(end_message, list) else end_message
    msg = MIMEText(end_message)
    msg['Subject'] = 'エンダーマンより'
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()  # TLSセキュリティを開始
        server.login(username, password)  # SMTPサーバにログイン
        server.send_message(msg)  # メールを送信
            
if __name__ == '__main__':
    try:
        if N_INC_INITIAL < 1:
            print("N_INC_INITIALは1以上に設定してください")
            sys.exit()
        sys.stdout.write("\033[?25l")

        # 並列実行
        manager = multiprocessing.Manager()
        lock = manager.Lock()
        cost_2D_origin = [[[] for _ in range(N_TRANS_INITIAL, N_TRANS_MAX + 1)] for _ in range(N_INC_INITIAL, N_INC_MAX + 1)]
        cost_2D = manager.list([manager.list([manager.list(item) for item in sublist]) for sublist in cost_2D_origin])    
        counter = manager.dict({i: 0 for i in range(N_INC_INITIAL, N_INC_MAX + 1)})
        
        start_time = time.perf_counter()
        current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        current_directory = os.path.dirname(os.path.abspath(__file__))
        
        def read_costlist_from_file(filepath):
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if len(lines) >= 36:
                    return eval(lines[35].strip())
            return None
        
        if restarting_output_directory == "":
            output_directory_name = f"{UNIT_TRANS}{waste_name}{N_INC_INITIAL}~{N_INC_MAX}&{N_TRANS_INITIAL}~{N_TRANS_MAX}{add_name}_{current_time}"
            output_directory = os.path.join(current_directory, output_directory_name)
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            tasks = [(count_inc, count_trans) for count_inc in range(N_INC_INITIAL, N_INC_MAX + 1) for count_trans in range(N_TRANS_INITIAL, N_TRANS_MAX + 1)]

        
        else:  # 中断入力時の再開
            output_directory_name = restarting_output_directory
            output_directory = os.path.join(current_directory, output_directory_name)
            if not os.path.exists(output_directory):
                print(f"指定された中断フォルダが存在しません。")
                sys.exit(1)
            # 既存のファイルから cost_2D と counter の状態を復元
            for n_inc in range(N_INC_INITIAL, N_INC_MAX + 1):
                for n_trans in range(N_TRANS_INITIAL, N_TRANS_MAX + 1):
                    filepath = os.path.join(output_directory, f"{waste_name}_{n_inc}&{n_trans}.txt")
                    if os.path.exists(filepath):
                        cost_list = read_costlist_from_file(filepath)
                        if cost_list is not None:
                                cost_2D[n_inc-N_INC_INITIAL][n_trans-N_TRANS_INITIAL] = cost_list
                                counter[n_inc] += 1
            # 中断入力時の未完了のタスク確認
            def check_completed_tasks(output_directory):
                completed_tasks = set()
                if os.path.exists(output_directory):
                    for filename in os.listdir(output_directory):
                        if filename.endswith(".txt") and "_" in filename and "&" in filename:
                            parts = filename.split("_")
                            inc_trans_part = parts[-1].replace(".txt", "").split("&")
                            if len(inc_trans_part) == 2:
                                try:
                                    inc, trans = map(int, inc_trans_part)
                                    completed_tasks.add((inc, trans))
                                except ValueError:
                                    continue
                return completed_tasks
        
            completed_tasks = check_completed_tasks(output_directory)  # 中断入力時は未完了のタスクのみを実行
            tasks = [(count_inc, count_trans) for count_inc in range(N_INC_INITIAL, N_INC_MAX + 1) for count_trans in range(N_TRANS_INITIAL, N_TRANS_MAX + 1) if (count_inc, count_trans) not in completed_tasks]        


        # フォルダ生成後すぐ自動git pull/push        
        subprocess.run(["git", "pull"], check=False)
        subprocess.run(["git", "add", "."], check=False)
        subprocess.run(["git", "commit", "-m", f"自動コミット(スタート):{UNIT_TRANS}{waste_name}{N_INC_INITIAL}~{N_INC_MAX}&{N_TRANS_INITIAL}~{N_TRANS_MAX}"], check=True)
        subprocess.run(["git", "push"], check=False)
        
        # 初期表示
        group_size = 3  # 一行に表示する進捗表示の数        
        for i in range(0, len(cost_2D), group_size):
            line_output = []
            for j in range(group_size):
                if i + j < len(cost_2D):
                    finish = cost_2D[i + j]
                    display_inc = i + j + N_INC_INITIAL
                    all_done = all(finish)  # すべてのトランザクションが完了しているかチェック
                    progress = [str(k + N_TRANS_INITIAL) if finish[k] else "@" for k in range(N_TRANS_MAX - N_TRANS_INITIAL + 1)]
                    display = ",".join(progress)
                    completion_status = "完" if all_done else "  "  # "完"またはスペースを選択
                    line_part = f"焼却{display_inc:2} → [{display}]{completion_status}"
                    line_output.append(line_part)
            sys.stdout.write("  ".join(line_output) + "\n")  # スペースを1つに縮小
        sys.stdout.write(waste_name + "\n")
        sys.stdout.flush()
        
        # 並列実行
        pool = multiprocessing.Pool()
        results = pool.starmap(multi_task, [(task, output_directory, current_time, lock, cost_2D, counter) for task in tasks])
        
        pool.close()
        pool.join()
        
        # 結果格納
        best_solutions = {}
        for count_inc, count_trans, fitness in results:
            best_solutions[(count_inc, count_trans)] = fitness
        #################################################################################

        optimal_count_inc = min(best_solutions, key=lambda x: best_solutions[x])[0]
        optimal_count_trans = min(best_solutions, key=lambda x: best_solutions[x])[1]
        optimal_file_name = f"{waste_name}_{optimal_count_inc}&{optimal_count_trans}.txt"
        new_file_name = f"{waste_name}_{optimal_count_inc}&{optimal_count_trans}_best.txt"
        optimal_file_path = os.path.join(output_directory, optimal_file_name)
        new_file_path = os.path.join(output_directory, new_file_name)
        os.rename(optimal_file_path, new_file_path)

        # 自動git pull/push
        subprocess.run(["git", "pull"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"自動コミット（終了）:{UNIT_TRANS}{waste_name}{N_INC_INITIAL}~{N_INC_MAX}&{N_TRANS_INITIAL}~{N_TRANS_MAX}"], check=True)
        subprocess.run(["git", "push"], check=True)
        
        print("\n" * len(cost_2D))
        print(f"最適な焼却＆中継施設数: {optimal_count_inc}&{optimal_count_trans} での総コスト: {best_solutions[optimal_count_inc,optimal_count_trans]}")

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"\n実行時間= {round(elapsed_time/3600,1)}h\n\n")
        sys.stdout.write("\033[?25h")

        end_message  = [output_directory_name,
                        f"最適な焼却＆中継施設数: {optimal_count_inc}&{optimal_count_trans} での総コスト: {best_solutions[optimal_count_inc,optimal_count_trans]}",
                        f"実行時間= {round(elapsed_time/3600,1)}h"
                        ]
        send_end_email(end_message)
    
    except Exception as e:
        error_message =  str(e)
        send_error_email(error_message)
        traceback.print_exc()