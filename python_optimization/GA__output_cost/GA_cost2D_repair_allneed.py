import os
import datetime

N_INC_INITIAL=1
N_INC_MAX=20
N_TRANS_INITIAL=0
N_TRANS_MAX=20
UNIT_TRANS=877
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

waste_name="kanen"

restarting_output_directory = "877kanen1~20&0~20_20240121_200306"


current_directory = os.path.dirname(os.path.abspath(__file__))
output_directory_name = restarting_output_directory
output_directory = os.path.join(current_directory, output_directory_name)


# _best.txtファイルの_bestを取り除く
for filename in os.listdir(output_directory):
    if filename.endswith("_best.txt"):
        new_filename = filename.replace("_best.txt", ".txt")
        os.rename(os.path.join(output_directory, filename), os.path.join(output_directory, new_filename))
        

def read_costlist_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        if len(lines) >= 36:
            return eval(lines[35].strip())
    return None

cost_2D = [[[] for _ in range(N_TRANS_INITIAL, N_TRANS_MAX + 1)] for _ in range(N_INC_INITIAL, N_INC_MAX + 1)]

for n_inc in range(N_INC_INITIAL, N_INC_MAX + 1):
    for n_trans in range(N_TRANS_INITIAL, N_TRANS_MAX + 1):
        filepath = os.path.join(output_directory, f"{waste_name}_{n_inc}&{n_trans}.txt")
        if os.path.exists(filepath):
            cost_list = read_costlist_from_file(filepath)
            if cost_list is not None:
                    cost_2D[n_inc-N_INC_INITIAL][n_trans-N_TRANS_INITIAL] = cost_list

print(f"inc{N_INC_MAX-N_INC_INITIAL+1} = {len(cost_2D)}")
for i in range(len(cost_2D)):
    print(f"trans[{i}]{N_TRANS_MAX-N_TRANS_INITIAL+1} = {len(cost_2D[i])-(cost_2D[i].count([]))}")
    
    
with open(os.path.join(output_directory, f"GA_Graph({UNIT_TRANS}{waste_name}){current_time}.txt"), 'w', encoding="utf-8") as file:
    file.write(f"#inc[{N_INC_INITIAL}~{N_INC_MAX}]&trans[{N_TRANS_INITIAL}~{N_TRANS_MAX}]\n")
    file.write(f'foldername = "{str(waste_name)}{str(UNIT_TRANS)}"\n')
    file.write(f"cost = {str(cost_2D)}\n")