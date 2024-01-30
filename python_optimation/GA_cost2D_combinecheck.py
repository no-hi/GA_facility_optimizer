import os
import glob
import re
import GA_function.GA_input as input
current_directory = os.path.dirname(os.path.abspath(__file__))
restarting_output_directory = os.path.join(current_directory, input.restarting_output_directory)

# 再開処理で作成したGA_GraphのGA_Graph名###############################
file_pattern_check = f"GA_Graph(877kanen)20240130_141013.txt"
#####################################################################

# フォルダ名から時間の部分を抽出（ない場合、名前の頭＝GA_Graphの先にあった方の（checkで作成するファイルではない方）ファイルを使う）
def find_file_with_time_pattern():
    match = re.search(r'\d{8}_\d{6}', restarting_output_directory)
    print(match)
    time_part = match.group(0)
    if time_part:
        file_pattern = f"*{time_part}*.txt"
        search_path = os.path.join(restarting_output_directory, file_pattern)
        file_list = glob.glob(search_path)
        if file_list:
            return file_list[0]  # リストの最初の要素を使用
    else:
        file_pattern = "GA_Graph*.txt"
        search_path = os.path.join(restarting_output_directory, file_pattern)
        file_list = glob.glob(search_path)
        return file_list[0]

# ファイル内の3行目の三次元costを取得
def read_costlist_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        cost_list = lines[2].strip()
        cost_list = cost_list.replace("cost = ", "")
        return eval(cost_list)

# 元々あったGA_Graphのcost
filepath_origin = find_file_with_time_pattern()
cost_origin = read_costlist_from_file(filepath_origin)

# 再開処理で作成したGA_Graphのcost
search_path = os.path.join(restarting_output_directory, file_pattern_check)
file_list = glob.glob(search_path)
filepath_check = file_list[0]
cost_check = read_costlist_from_file(filepath_check)

# リストの比較
def are_equal_3d_lists(list1, list2):
    if len(list1) != len(list2):
        return False
    for i in range(len(list1)):
        if len(list1[i]) != len(list2[i]):
            return False
        for j in range(len(list1[i])):
            if len(list1[i][j]) != len(list2[i][j]):
                return False
            for k in range(len(list1[i][j])):
                if list1[i][j][k] != list2[i][j][k]:
                    return False
    return True

print(are_equal_3d_lists(cost_origin, cost_check))