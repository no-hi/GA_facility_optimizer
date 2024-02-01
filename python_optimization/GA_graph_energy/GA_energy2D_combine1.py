import datetime
from collections import defaultdict
import python_optimation.GA_graph_energy.GA_energy2D__input as energylist
current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

########################################################################
info_component = ["inc[1~20]&trans[0~10]", "inc[21~25]&trans[0~10]"]
goal = "inc[1~25]&trans[0~10]"
filename = f"GA_graph_energy2D{goal.replace('[','').replace(']','').replace('inc','').replace('trans','')}_{current_time}.txt"
energy_component = energylist.energy_component
########################################################################

class FacilityListMerger:
    def __init__(self, energy_component, info_component, goal):   
        self.energy_component = energy_component
        self.info_component = info_component
        self.goal = self._parse_range(goal)
    
    def _parse_range(self, range_str):   
        range_dict = {}
        for part in range_str.split('&'):
            key, value = part.split('[')
            start, end = map(int, value.strip(']').split('~'))
            range_dict[key] = (start, end)
        return range_dict

    def _is_within_goal(self, info_range):  
        for key, (start, end) in info_range.items():
            goal_start, goal_end = self.goal[key]
            if start < goal_start or end > goal_end:
                return False
        return True

    def _sum_list(self, list):
        return sum(list)

    def _compare_and_choose_list(self, list1, list2):
        sum_list1 = self._sum_list(list1)
        sum_list2 = self._sum_list(list2)
        return list1 if sum_list1 < sum_list2 else list2

    def merge_lists(self):
        merged_result = []
        missing_ranges = defaultdict(list)
        conflict_info = defaultdict(lambda: {"winner": None, "loser": None, "battle_fields": []})
        
        for i, (info1, first_level_list1) in enumerate(zip(self.info_component, self.energy_component)):
            parsed_info1 = self._parse_range(info1)
            if not self._is_within_goal(parsed_info1):
                continue

            overlap_found = False
            for j in range(len(self.info_component)):
                if i == j:
                    continue  # 同じリストとの比較はスキップ
                info2 = self.info_component[j]
                first_level_list2 = self.energy_component[j]
                parsed_info2 = self._parse_range(info2)

                if not self._is_within_goal(parsed_info2):
                    continue

                # 重なる範囲の特定
                overlap_inc_start = max(parsed_info1['inc'][0], parsed_info2['inc'][0])
                overlap_inc_end = min(parsed_info1['inc'][1], parsed_info2['inc'][1])
                overlap_trans_start = max(parsed_info1['trans'][0], parsed_info2['trans'][0])
                overlap_trans_end = min(parsed_info1['trans'][1], parsed_info2['trans'][1])

                # 重なる範囲が存在する場合、比較を行う
                if overlap_inc_start <= overlap_inc_end and overlap_trans_start <= overlap_trans_end:
                    overlap_found = True
                    for inc_index in range(overlap_inc_start, overlap_inc_end + 1):
                        inc_pos1 = inc_index - parsed_info1['inc'][0]
                        inc_pos2 = inc_index - parsed_info2['inc'][0]
                        for trans_index in range(overlap_trans_start, overlap_trans_end + 1):
                            trans_pos1 = trans_index - parsed_info1['trans'][0]
                            trans_pos2 = trans_index - parsed_info2['trans'][0]

                            data_list1 = first_level_list1[inc_pos1][trans_pos1] if inc_pos1 < len(first_level_list1) and trans_pos1 < len(first_level_list1[inc_pos1]) else []
                            data_list2 = first_level_list2[inc_pos2][trans_pos2] if inc_pos2 < len(first_level_list2) and trans_pos2 < len(first_level_list2[inc_pos2]) else []

                            if data_list1 and data_list2:
                                chosen_list = self._compare_and_choose_list(data_list1, data_list2)
                                merged_result.append(chosen_list)
                                winner = info1 if chosen_list == data_list1 else info2
                                loser = info2 if chosen_list == data_list1 else info1
                                conflict_info[inc_index]["winner"] = winner
                                conflict_info[inc_index]["loser"] = loser
                                conflict_info[inc_index]["battle_fields"].append(f"{inc_index}&{trans_index}")

                                
            # 重なる範囲が存在しない場合、リストをそのまま追加
            if not overlap_found:
                for inc_index, second_level_list in enumerate(first_level_list1):
                    for trans_index, data_list in enumerate(second_level_list):
                        if data_list and not all(value == 0 for value in data_list):
                            merged_result.append(data_list)

        formatted_conflict_info = [{"winner": info["winner"], "loser": info["loser"], "battle_fields": info["battle_fields"]} for info in conflict_info.values()]
        
        return merged_result, missing_ranges, formatted_conflict_info


merger = FacilityListMerger(energy_component, info_component, goal)
merged_result, missing_ranges, formatted_conflict_info = merger.merge_lists()


with open(filename, "w") as file:
    print([merged_result], file=file)
    
print("Missing Ranges:", missing_ranges)
print("Conflict Information:", formatted_conflict_info)

