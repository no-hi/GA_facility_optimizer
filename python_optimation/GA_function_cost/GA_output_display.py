import multiprocessing
import sys
import os
import subprocess
import time
import data
import GA_function_cost.GA_input as input

waste_name = input.waste_name
N_INC_INITIAL = input.N_INC_INITIAL
N_INC_MAX = input.N_INC_MAX
N_TRANS_INITIAL = input.N_TRANS_INITIAL
N_TRANS_MAX = input.N_TRANS_MAX
N_GEN = input.N_GEN 
UNIT_TRANS = input. UNIT_TRANS
# TOP_N_CITIES = N_INC + N_TRANS +10          # ごみ量順位下限→ループ内で設定

hokkaido = data.name
waste = getattr(data, waste_name)

#情報表示###############################################################################################################
def output_info(N_INC, N_TRANS, N_IND, get_top_cities, total_cost_info, gen_info, sumgen, hof, start_time_count, current_time, output_directory, lock, cost_2D, counter):    
    
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
    
    with lock: # 共有化されたcost2Dやparallel.counterをいじるときはlockをかける
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