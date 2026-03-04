import numpy as np
sensitivity = 0.3
a = np.array([1, -1, 0.95, 0.98, 1.02, -1.1, -0.99, 1.7])
differences = np.diff(a)
print(differences)
diff_above_threshold = differences > (2-sensitivity)
print(diff_above_threshold)
# start_inx = np.argmin(diff_above_threshold)
# print(start_inx)
# idx = np.where(differences > (2-sensitivity))[0][0] 
# print(idx)
idx = np.argmax(diff_above_threshold)
print(idx)
if differences[idx] > 2 - sensitivity:
    # We found preamble!
    print(differences[idx])
else:
    # No preamble
    pass