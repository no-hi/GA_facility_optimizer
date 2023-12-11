    def repair(individual):
        unused = individual.unused_cities
        combined = individual.inc_facility + individual.trans_facility
        
        # 重複要素を置き換える
        # 重複している要素ごとに、保持するインスタンスをランダムに選択
        facility_count = collections.Counter(combined)
        to_replace = {}
        for facility in facility_count:
            if facility_count[facility] > 1:
                # 重複しているインデックスを全て見つける
                indices = [i for i, x in enumerate(combined) if x == facility]
                # 一つをランダムに選んで保持し、他は置き換え対象とする
                keep = random.choice(indices)
                to_replace[facility] = [idx for idx in indices if idx != keep]
        # 置き換え対象のインデックスに対して、unusedから要素を選んで置き換え
        for facility, indices in to_replace.items():
            for i in indices:
                if unused:  # unusedが空でないことを確認
                    new_facility = random.choice(list(unused))
                    unused.remove(new_facility)
                    combined[i] = new_facility

        new_unused = list(set(range(N_CITIES)) - set(combined))

        individual.inc_facility = combined[:N_INC]
        individual.trans_facility = combined[N_INC:N_INC + N_TRANS]
        individual.unused_cities = new_unused
        individual[:] = individual.inc_facility + individual.trans_facility
        
        return individual

    toolbox.register("repair", repair)
