from copy import deepcopy
import GA_function_energy.GA_input_energy as input

def local_optimization(best_individual, total_energy):
    current_best = best_individual
    current_best_score, *_ = total_energy(best_individual)
    
    # Inc遺伝子の全通り計算
    fixed_inc_indices = set()
    while True:
        new_best_found = False
        for i in range(len(current_best.inc_facility)):
            if i in fixed_inc_indices:
                continue  # 変更された遺伝子位置はスキップ
            for new_inc in range(input.N_CITIES):
                # new_incが他の遺伝子で使われていないかチェック
                if new_inc in current_best.inc_facility[:i] + current_best.inc_facility[i+1:] or new_inc in current_best.trans_facility:
                    continue
                individual = deepcopy(current_best)
                individual.inc_facility[i] = new_inc
                score, *_ = total_energy(individual)
                if score < current_best_score:
                    current_best = individual
                    current_best_score = score
                    new_best_found = True
                    fixed_inc_indices.add(i)  # 新しい最適遺伝子を固定
        if not new_best_found:
            # 新しい最適解が見つからなければループを終了
            break

    # Trans遺伝子の全通り計算
    fixed_trans_indices = set()  # 固定されたtrans遺伝子のインデックスを保持
    while True:
        new_best_found = False
        for i in range(len(current_best.trans_facility)):
            if i in fixed_trans_indices:
                continue  # 既に最適と判断された遺伝子はスキップ
            for new_trans in range(input.N_CITIES):
                # 新しい遺伝子が他のtrans遺伝子やinc遺伝子で使われていないかチェック
                if new_trans in current_best.trans_facility[:i] + current_best.trans_facility[i+1:] or new_trans in current_best.inc_facility:
                    continue
                individual = deepcopy(current_best)
                individual.trans_facility[i] = new_trans
                score, *_ = total_energy(individual)
                if score < current_best_score:
                    current_best = individual
                    current_best_score = score
                    new_best_found = True
                    fixed_trans_indices.add(i)  # 新しい最適遺伝子を固定
        if not new_best_found:
            # 新しい最適解が見つからなければループを終了
            break
    
    
    # 最適個体の属性修正
    new_individual = deepcopy(best_individual)
    new_individual.inc_facility = current_best.inc_facility
    new_individual.trans_facility = current_best.trans_facility
    new_individual.unused_cities = set(range(input.N_CITIES)) - set(new_individual.inc_facility) - set(new_individual.trans_facility)
    new_individual.fitness.values = [current_best_score]
    
    
    return new_individual
