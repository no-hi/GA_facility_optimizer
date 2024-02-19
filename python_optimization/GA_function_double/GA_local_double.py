from copy import deepcopy
import GA_function_double.GA_input_double as input


def local_optimization(best_individual, total_cost, cities_zero):
    current_best = best_individual
    current_best_score, *_ = total_cost(best_individual)
        
    # 遺伝子全通り計算
    fixed_indices = set()
    while True:
        new_best_found = False
        facilities = current_best.inc_facility + current_best.trans_facility
        for i in range(len(facilities)):
            if i in fixed_indices:
                continue  # 変更された遺伝子位置はスキップ
            for new_facility in [city for city in list(current_best.unused_cities) if city not in cities_zero] :
                if new_facility in facilities[:i] + facilities[i+1:]:
                    continue
                individual = deepcopy(current_best)
                if i < len(current_best.inc_facility):
                    individual.inc_facility[i] = new_facility
                else:
                    individual.trans_facility[i - len(current_best.inc_facility)] = new_facility

                score, *_ = total_cost(individual)
                if score < current_best_score:
                    current_best = individual
                    current_best_score = score
                    if i < len(current_best.inc_facility):
                        facilities[i] = new_facility
                        current_best.inc_facility[i] = new_facility
                    else:
                        facilities[i - len(current_best.inc_facility)] = new_facility
                        current_best.trans_facility[i - len(current_best.inc_facility)] = new_facility
                    current_best.unused_cities = set(range(input.N_CITIES)) - set(current_best.inc_facility) - set(current_best.trans_facility)
                    new_best_found = True
                    fixed_indices.add(i)  # 新しい最適遺伝子を固定
        if not new_best_found:
            break
    
    # 最適個体の属性修正
    new_individual = deepcopy(best_individual)
    new_individual.inc_facility = current_best.inc_facility
    new_individual.trans_facility = current_best.trans_facility
    new_individual.unused_cities = set(range(input.N_CITIES)) - set(new_individual.inc_facility) - set(new_individual.trans_facility)
    new_individual.fitness.values = [current_best_score]
        
        
    return new_individual


