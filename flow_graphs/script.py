import numpy as np
from scipy import signal
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

file_path = "/home/sdr/final_project_SDR/gr-ori_omer/flow_graphs/temp_output.txt"

# file_path = "/home/sdr/final_project_SDR/gr-ori_omer/flow_graphs/temp_moded.txt"


with open(file_path, "rb") as f:
    vec = np.fromfile(f, dtype=np.float32)

preamble_voltages = -1 * np.ones(int(32000 * 0.1))

corr = signal.correlate(vec, preamble_voltages)
corr = np.round(corr, 2)
peaks, _ = find_peaks(corr, distance=1600, height=(32000*0.1*0.5))

print("all the peaks", peaks)
if len(peaks) > 0:
    print("preamble ends at", peaks[0])

plt.figure()
# plt.plot(corr, label='signal')
# plt.plot(peaks, corr[peaks], "x", color = 'r', label='detected_peaks')
plt.plot(vec)
plt.show()