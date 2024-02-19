class Fitness:
    def __init__(self):
        self.values = []

class Individual:
    def __init__(self):
        self.inc_facility = []
        self.trans_facility = []
        self.unused_cities = []
        self.fitness = Fitness()

# 使用例
individual = Individual()
individual.inc_facility = [1, 2, 3]
individual.trans_facility = [4, 5, 6]
individual.unused_cities = [7, 8, 9]
individual.fitness.values = [10, 11, 12]
