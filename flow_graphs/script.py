import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

file_path = "/home/sdr/final_project_SDR/gr-ori_omer/flow_graphs/temp_output.txt"

# file_path = "/home/sdr/final_project_SDR/gr-ori_omer/flow_graphs/temp_moded.txt"


with open(file_path, "rb") as f:
    vec = np.fromfile(f, dtype=np.float32)

preamble_voltages = -1 * np.ones(int(32000 * 0.1))

corr = signal.correlate(vec, preamble_voltages)
corr = np.round(corr, 2)
print("corr", corr)
print("peak", np.argmax(corr))
# max_value = np.amax(corr)
# peak_indexes = np.argwhere(corr == max_value)
# print("max corr", max_value, "at", peak_indexes.flatten().tolist())

plt.figure()
plt.plot(corr)
plt.show()

# print(vec)
# print(np.size(vec))

# vec = vec[0:100]
# plt.plot(vec.real, vec.imag)

# plt.show()