[1 1 -1] -> 0.3
[1 -1 -1] -> -0.3
avg with only noise~0

0.6 diff

self.preamble_length = int(fs*t)
self.SPS = int(3*fs*t)

diff = np.diff(in0)

sensitivity = 0.3
# [0.2 0.4 1 -0.3 2.1 0.2 -1.8 2.3]
start_inx = np.argmin(diff > (2-sensitivity)) # [0 0 0 0 1 0 0 1]

# [2.1 0.2 -1.8 2.3]
diff = diff[start_inx:] # cut off the start
diff = diff.reshape((-1, self.SPS))
[1 2 3
 4 5 6]

voltage_averages = np.average(diff)
[ 2
 5]

diff = diff.reshape((1,-1))

diff(diff > 0.2) = 1
diff(diff < -0.2) = 0