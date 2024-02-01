from copy import deepcopy
import GA_function_cost.GA_input_cost as input

def local_optimization(best_individual, total_cost):
    current_best = best_individual
    current_best_score, *_ = total_cost(best_individual)
    
    # 遺伝子全通り計算
    while True:
        new_best_found = False
        facilities = current_best.inc_facility + current_best.trans_facility
        for i in range(len(facilities)):
            for new_facility in range(input.N_CITIES):
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
                    new_best_found = True
        if not new_best_found:
            break
    
    
    # 最適個体の属性修正
    new_individual = deepcopy(best_individual)
    new_individual.inc_facility = current_best.inc_facility
    new_individual.trans_facility = current_best.trans_facility
    new_individual.unused_cities = set(range(input.N_CITIES)) - set(new_individual.inc_facility) - set(new_individual.trans_facility)
    new_individual.fitness.values = [current_best_score]
    
    
    return new_individual
