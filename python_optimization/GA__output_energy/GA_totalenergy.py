import os
import datetime

N_INC_INITIAL=1
N_INC_MAX=35
N_TRANS_INITIAL=0
N_TRANS_MAX=20
UNIT_TRANS=877
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

waste_name="kanen"

restarting_output_directory = "4.8sanpai1~35&0~20_20240130_150350"


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

total_2D = [[[] for _ in range(N_TRANS_INITIAL, N_TRANS_MAX + 1)] for _ in range(N_INC_INITIAL, N_INC_MAX + 1)]

for n_inc in range(N_INC_INITIAL, N_INC_MAX + 1):
    for n_trans in range(N_TRANS_INITIAL, N_TRANS_MAX + 1):
        filepath = os.path.join(output_directory, f"{waste_name}_{n_inc}&{n_trans}.txt")
        if os.path.exists(filepath):
            energy_list = read_costlist_from_file(filepath)
            totalenergy = sum(energy_list)
            if totalenergy is not None:
                    total_2D[n_inc-N_INC_INITIAL][n_trans-N_TRANS_INITIAL] = totalenergy

print(f"inc{N_INC_MAX-N_INC_INITIAL+1} = {len(total_2D)}")
for i in range(len(total_2D)):
    print(f"trans[{i}]{N_TRANS_MAX-N_TRANS_INITIAL+1} = {len(total_2D[i])-(total_2D[i].count([]))}")
    
    
with open(os.path.join(output_directory, f"_totalenergy({UNIT_TRANS}{waste_name}){current_time}.txt"), 'w', encoding="utf-8") as file:
    file.write(f"#inc[{N_INC_INITIAL}~{N_INC_MAX}]&trans[{N_TRANS_INITIAL}~{N_TRANS_MAX}]\n")
    file.write(f'foldername = "{str(waste_name)}{str(UNIT_TRANS)}"\n')
    file.write(f"totalenergy = {str(total_2D)}\n")