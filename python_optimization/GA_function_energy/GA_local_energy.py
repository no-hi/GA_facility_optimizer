from copy import deepcopy
import GA_function_energy.GA_input_energy as input

def local_optimization(best_individual, total_energy):
    current_best = best_individual
    current_best_score, *_ = total_energy(best_individual)
        
    with open('print.txt', 'w') as file:
        # 遺伝子全通り計算
        fixed_indices = set()
        while True:
            new_best_found = False
            facilities = current_best.inc_facility + current_best.trans_facility
            print("Current facilities:", facilities, file=file)  # 現在のfacilitiesの状態を出力
            for i in range(len(facilities)):
                if i in fixed_indices:
                    continue  # 変更された遺伝子位置はスキップ
                for new_facility in range(input.N_CITIES):
                    if new_facility in facilities[:i] + facilities[i+1:]:
                        continue
                    individual = deepcopy(current_best)
                    print("Before change:", individual.inc_facility, individual.trans_facility, file=file)  # 変更前のindividualの状態を出力
                    if i < len(current_best.inc_facility):
                        individual.inc_facility[i] = new_facility
                    else:
                        individual.trans_facility[i - len(current_best.inc_facility)] = new_facility
                    print("After change:", individual.inc_facility, individual.trans_facility, file=file)  # 変更後のindividualの状態を出力

                    score, *_ = total_energy(individual)
                    if score < current_best_score:
                        current_best = individual
                        current_best_score = score
                        new_best_found = True
                        fixed_indices.add(i)  # 新しい最適遺伝子を固定
                        print("Updated current_best:", current_best.inc_facility, current_best.trans_facility, file=file)  # 更新後のcurrent_bestの状態を出力
            if not new_best_found:
                break
            print("Fixed indices:", fixed_indices, file=file)  # fixed_indicesの状態を出力
    
        # 最適個体の属性修正
        new_individual = deepcopy(best_individual)
        new_individual.inc_facility = current_best.inc_facility
        new_individual.trans_facility = current_best.trans_facility
        new_individual.unused_cities = set(range(input.N_CITIES)) - set(new_individual.inc_facility) - set(new_individual.trans_facility)
        new_individual.fitness.values = [current_best_score]
        
        print("Final new_individual:", new_individual.inc_facility, new_individual.trans_facility, file=file)  # 最終的なnew_individualの状態を出力
        
    return new_individual
