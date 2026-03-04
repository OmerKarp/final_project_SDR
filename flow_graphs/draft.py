import numpy as np


a = np.array([-2, -2, -2])

m1 = np.array([True, False, False])
m2 = np.array([False, True, True])

a[m1] = 1
a[m2] = 0
print(a)