import numpy as np

# リスト合成####################################################################

cost1 = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
cost2 = [[[9, 10], [11, 12]], [[13, 14], [15, 16]]]

array1 = np.array(cost1)
array2 = np.array(cost2)
combined_array = np.concatenate((array1, array2), axis=0)
combined_list = combined_array.tolist()

##############################################################################