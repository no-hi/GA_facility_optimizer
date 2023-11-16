for inc_key in trans_to_inc:
                if sum(yearly_trans_size[best_individual.trans_facility.index(trans)] for trans in trans_to_inc[inc_key]) > 0:
                    output_content.append(f"indirect {hokkaido[inc_key]}({sum(yearly_trans_size[best_individual.trans_facility.index(trans)] for trans in trans_to_inc[inc_key])})/{inc_size} → receive from: {trans_to_inc_names}")

中継→焼却のキーについて、
もし、解の中継の番号それぞれの中継規模合計が0より大きいとき、
アウトプットにindirect北海道の焼却番号：合計中継規模