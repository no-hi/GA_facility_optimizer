def sort_facility(facility, size_list, cities_to__):
    sorted_facilities = sorted(
        [(i, size) for i, size in enumerate(size_list)], 
        key=lambda x: x[1], 
        reverse=True
    )
    formatted_output = []
    for i, size in sorted_facilities:
        facility_name = hokkaido[facility[i]]
        cities__ = ', '.join([hokkaido[city] for city in cities_to__[facility[i]]])
        formatted_output.append(f"{facility_name} ({size}) → receive from: {cities__}")
    return formatted_output

# 以下の部分はメインの処理部分で使用します
# ごみ量ソート
top_cities_info = [f"hokkaido[i]} ({waste[i]})" for i in get_top_cities()]
output_content.append("ごみ量" + str(TOP_N_CITIES) + "位以内：")
output_content.append(", ".join(top_cities_info))

# 焼却施設情報
output_content.append("\n焼却施設数: " + str(len(best_individual.inc_facility)))
output_content.extend(sort_facility(best_individual.inc_facility, yearly_inc_size, cities_to_inc))

# 中継施設情報
output_content.append("\n中継施設数: " + str(len(best_individual.trans_facility)))
output_content.extend(sort_facility(best_individual.trans_facility, yearly_trans_size, cities_to_trans))

# コスト情報などの出力は元のコードを維持

# ファイルに書き込む
write_to_file(output_file_path, '\n'.join(output_content))
