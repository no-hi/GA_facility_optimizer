import os
import time
import datetime
import multiprocessing
from itertools import product
import sys
import subprocess
import traceback
import GA_function_double.GA_input_double as input
import GA_function_double.GA_optimization_double as GA
import GA_function_double.GA_mail as mail


add_name = input.add_name
waste_name = input.waste_name
N_INC_INITIAL = input.N_INC_INITIAL
N_INC_MAX = input.N_INC_MAX
N_TRANS_INITIAL = input.N_TRANS_INITIAL
N_TRANS_MAX = input.N_TRANS_MAX
UNIT_energy_TRANS = input. UNIT_energy_TRANS
restarting_output_directory = input.restarting_output_directory
# TOP_N_CITIES = N_INC + N_TRANS +10          # ごみ量順位下限→ループ内で設定

# 並列実行########################################################################
def multi_task(task, current_time, output_directory, lock, double_2D, counter,energy_2D,cost_2D):
    count_inc, count_trans = task
    best_individual = GA.GA_optimization(count_inc, count_trans, current_time, output_directory, lock, double_2D, counter,energy_2D,cost_2D)
    return count_inc, count_trans, best_individual.fitness.values[0]

if __name__ == '__main__':
    try:
        if N_INC_INITIAL < 1:
            print("N_INC_INITIALは1以上に設定してください")
            sys.exit()
        sys.stdout.write("\033[?25l")
        
        # 並列初期設定
        manager = multiprocessing.Manager()
        lock = manager.Lock()
        double_2D_origin = [[[] for _ in range(N_TRANS_INITIAL, N_TRANS_MAX + 1)] for _ in range(N_INC_INITIAL, N_INC_MAX + 1)]
        double_2D = manager.list([manager.list([manager.list(item) for item in sublist]) for sublist in double_2D_origin]) 
        cost_2D_origin = [[[] for _ in range(N_TRANS_INITIAL, N_TRANS_MAX + 1)] for _ in range(N_INC_INITIAL, N_INC_MAX + 1)]
        cost_2D = manager.list([manager.list([manager.list(item) for item in sublist]) for sublist in double_2D_origin])
        energy_2D_origin = [[[] for _ in range(N_TRANS_INITIAL, N_TRANS_MAX + 1)] for _ in range(N_INC_INITIAL, N_INC_MAX + 1)]
        energy_2D = manager.list([manager.list([manager.list(item) for item in sublist]) for sublist in double_2D_origin])      
        counter = manager.dict({i: 0 for i in range(N_INC_INITIAL, N_INC_MAX + 1)})
        best_solutions = {(n_inc, n_trans): None for n_inc in range(N_INC_INITIAL, N_INC_MAX + 1) for n_trans in range(N_TRANS_INITIAL, N_TRANS_MAX + 1)}
        
        start_time = time.perf_counter()
        current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        current_directory = os.path.dirname(os.path.abspath(__file__))
        
        def read_doublelist_from_file(filepath):
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if len(lines) >= 36:
                    return eval(lines[35].strip())
            return None
        
        if restarting_output_directory == "":
            output_directory_name = f"{UNIT_energy_TRANS}{waste_name}{N_INC_INITIAL}~{N_INC_MAX}&{N_TRANS_INITIAL}~{N_TRANS_MAX}{add_name}_{current_time}"
            output_directory = os.path.join(current_directory, "GA__output_double", output_directory_name)
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            # フォルダ生成後すぐ自動git pull/push        
            subprocess.run(["git", "pull"], check=False)
            subprocess.run(["git", "add", "."], check=False)
            subprocess.run(["git", "commit", "-m", f"自動コミット(コストスタート):{UNIT_energy_TRANS}{waste_name}{N_INC_INITIAL}~{N_INC_MAX}&{N_TRANS_INITIAL}~{N_TRANS_MAX}"], check=False)
            subprocess.run(["git", "push"], check=False)
            tasks = [(count_inc, count_trans) for count_inc in range(N_INC_INITIAL, N_INC_MAX + 1) for count_trans in range(N_TRANS_INITIAL, N_TRANS_MAX + 1)]
            
        
        else:  # 中断入力時の再開
            output_directory_name = restarting_output_directory
            output_directory = os.path.join(current_directory, "GA__output_double", output_directory_name)
            if not os.path.exists(output_directory):
                print(f"指定された中断フォルダが存在しません。")
                sys.exit(1)
            # フォルダ生成後すぐ自動git pull/push        
            subprocess.run(["git", "pull"], check=False)
            subprocess.run(["git", "add", "."], check=False)
            subprocess.run(["git", "commit", "-m", f"自動コミット(コストスタート):{UNIT_energy_TRANS}{waste_name}{N_INC_INITIAL}~{N_INC_MAX}&{N_TRANS_INITIAL}~{N_TRANS_MAX}"], check=False)
            subprocess.run(["git", "push"], check=False)
            # _best.txtファイルの_bestを取り除く
            for filename in os.listdir(output_directory):
                if filename.endswith("_best.txt"):
                    new_filename = filename.replace("_best.txt", ".txt")
                    os.rename(os.path.join(output_directory, filename), os.path.join(output_directory, new_filename))
            # 既存のファイルから double_2D と counter の状態を復元
            for n_inc in range(N_INC_INITIAL, N_INC_MAX + 1):
                for n_trans in range(N_TRANS_INITIAL, N_TRANS_MAX + 1):
                    filepath = os.path.join(output_directory, f"{waste_name}_{n_inc}&{n_trans}.txt")
                    if os.path.exists(filepath):
                        double_list = read_doublelist_from_file(filepath)
                        if double_list is not None:
                                double_2D[n_inc-N_INC_INITIAL][n_trans-N_TRANS_INITIAL] = double_list
                                counter[n_inc] += 1
                                # 不足fitness補充
                                best_solutions[(n_inc, n_trans)] = sum(double_list)
                                
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
            
        
        # 初期表示
        if N_TRANS_MAX - N_TRANS_INITIAL +1 > 20:
            group_size = 2  # 一行に表示する進捗表示の数
        else:
            group_size = 3  # 一行に表示する進捗表示の数          
        for i in range(0, len(double_2D), group_size):
            line_output = []
            for j in range(group_size):
                if i + j < len(double_2D):
                    finish = double_2D[i + j]
                    display_inc = i + j + N_INC_INITIAL
                    all_done = all(finish)  # すべてのトランザクションが完了しているかチェック
                    progress = [str(k + N_TRANS_INITIAL) if finish[k] else "@" for k in range(N_TRANS_MAX - N_TRANS_INITIAL + 1)]
                    display = ",".join(progress)
                    completion_status = "完" if all_done else "  "  # "完"またはスペースを選択
                    line_part = f"焼却{display_inc:2} → [{display}]{completion_status}"
                    line_output.append(line_part)
            sys.stdout.write("  ".join(line_output) + "\n")  # スペースを1つに縮小
        sys.stdout.write(f"double({waste_name})\n")
        sys.stdout.flush()
        
        # 並列実行
        pool = multiprocessing.Pool()
        results = pool.starmap(multi_task, [(task, current_time, output_directory, lock, double_2D, counter,energy_2D,cost_2D) for task in tasks])
        
        pool.close()
        pool.join()
        
        # 結果格納
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
        subprocess.run(["git", "commit", "-m", f"自動コミット（コスト終了）:{UNIT_energy_TRANS}{waste_name}{N_INC_INITIAL}~{N_INC_MAX}&{N_TRANS_INITIAL}~{N_TRANS_MAX}"], check=True)
        subprocess.run(["git", "push"], check=True)
        
        print("\n" * len(double_2D))
        print(f"最適な焼却＆中継施設数: {optimal_count_inc}&{optimal_count_trans} での総コスト: {best_solutions[optimal_count_inc,optimal_count_trans]}")

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"\n実行時間= {round(elapsed_time/3600,1)}h\n\n")
        sys.stdout.write("\033[?25h")

        end_message  = [output_directory_name,
                        f"最適な焼却＆中継施設数: {optimal_count_inc}&{optimal_count_trans} での総コスト: {best_solutions[optimal_count_inc,optimal_count_trans]}",
                        f"実行時間= {round(elapsed_time/3600,1)}h"
                        ]
        mail.send_end_email(end_message,output_directory_name)
        
    except Exception as e:
        output_directory_name=f"{waste_name}{N_INC_INITIAL}~{N_INC_MAX}&{N_TRANS_INITIAL}~{N_TRANS_MAX}"
        error_message = [output_directory_name,
                        str(e)
                        ]
        mail.send_error_email(error_message,output_directory_name)
        traceback.print_exc()