from copy import deepcopy
import GA_function_energy.GA_input_energy as input

def local_optimization(best_individual, total_energy):
    current_best = best_individual
    current_best_score, *_ = total_energy(best_individual)
    
    print(best_individual.inc_facility, best_individual.trans_facility )
    
    # 遺伝子全通り計算
    fixed_indices = set()
    while True:
        new_best_found = False
        facilities = current_best.inc_facility + current_best.trans_facility
        for i in range(len(facilities)):
            if i in fixed_indices:
                continue  # 変更された遺伝子位置はスキップ
            for new_facility in range(input.N_CITIES):
                if new_facility in facilities[:i] + facilities[i+1:]:
                    continue
                individual = deepcopy(current_best)
                if i < len(current_best.inc_facility):
                    individual.inc_facility[i] = new_facility
                else:
                    individual.trans_facility[i - len(current_best.inc_facility)] = new_facility

                score, *_ = total_energy(individual)
                if score < current_best_score:
                    current_best = individual
                    current_best_score = score
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
    
    print(new_individual.inc_facility, new_individual.trans_facility )
    
    
    return new_individual

    
