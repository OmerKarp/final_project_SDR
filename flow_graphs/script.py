import numpy as np
import matplotlib.pyplot as plt

file_path = "/home/sdr/final_project_SDR/gr-ori_omer/flow_graphs/temp_output.txt"

with open(file_path, "rb") as f:
    vec = np.fromfile(f, dtype=np.float32)

print(vec)
print(np.size(vec))

plt.plot(vec)

plt.show()