from deap import base, creator, tools, algorithms
import random
import numpy as np
import time
import iburidata as iburidata

start_time = time.perf_counter()

# Import data
hokkaido = iburidata.name
kanen = iburidata.kanen
distance = iburidata.distance

# Convert distances into 2D array
distance = np.array(distance).reshape(len(hokkaido), len(hokkaido))

print(distance)