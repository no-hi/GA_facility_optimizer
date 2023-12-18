import os

# リストを事前に初期化
total_cost_list = TC_direct_list = IC_inc_list = OC_inc_list = TC_indirect_list = IC_trans_list = OC_trans_list = [[] for _ in range(N_TRANS_MAX + 1)]

# メインの処理
with open(os.path.join(output_directory, f"GAGraph{UNIT_TRANS}{waste_name}_{current_time}.txt"), 'a', encoding="utf-8") as file:
    if N_INC == N_INC_INITIAL and N_TRANS == N_TRANS_INITIAL:
        file.write(f"（inc{N_INC_INITIAL}+trans{N_TRANS_INITIAL}～）コスト行列\n")
        # 条件に応じてリストを再初期化
        total_cost_list = TC_direct_list = IC_inc_list = OC_inc_list = TC_indirect_list = IC_trans_list = OC_trans_list = [[] for _ in range(N_TRANS_MAX + 1)]
    
    # 各リストにデータを追加
    data_values = [total_cost_, TC_direct_values, IC_inc_values, OC_inc_values, TC_indirect_values, IC_trans_values, OC_trans_values]
    lists = [total_cost_list, TC_direct_list, IC_inc_list, OC_inc_list, TC_indirect_list, IC_trans_list, OC_trans_list]
    
    for list_, value in zip(lists, data_values):
        list_[N_TRANS].append(value)

    # 各リストの内容をファイルに出力
    list_names = ['total_cost_list', 'TC_direct_list', 'IC_inc_list', 'OC_inc_list', 'TC_indirect_list', 'IC_trans_list', 'OC_trans_list']
    for list_name, list_content in zip(list_names, lists):
        file.write(f"{list_name} = {str(list_content)}\n")
