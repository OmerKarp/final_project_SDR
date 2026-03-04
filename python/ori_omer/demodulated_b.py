#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2026 omer_ori.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
from collections import deque

class demodulated_b(gr.sync_block):
    """
    docstring for block demodulated_b
    """
    def __init__(self, t=1, fs=1000,sens=1,timeout_seconds=3):
        gr.sync_block.__init__(self,
            name="demodulated_b",
            in_sig=[np.float32],
            out_sig=None)
        self._t=t
        self._fs=fs
        self._sens = sens

        self._SPS = 3*fs*t        # <number of samples per second> * <time that a 1/3 symbol is transmitted>
        self._preabmle_number_of_samples = fs*t   # the preabmle is only t and not 3t time units

        self._num_of_noise_samples = 0
        self._is_listening = False
        self._num_of_noise_samples_threshold = fs*timeout_seconds

    def work(self, input_items, output_items):
        in0 = input_items[0]

        diff = np.diff(in0)
        # [-1 11-1 1-1-1] -> [2 0 -2 2 -2 0]
        # 2 Represents the beginning of a bit, the location of -2 marks if it's 0 or 1
        # 2 -2 0 -> 0
        # 2 0 -2 -> 1

        # demodulated_data = 
        # bit_starting_indexes = diff(diff > (2-self._sens))
        # drop_indexes = (diff(diff < -(2-self._sens)))  

        bits_avg_diff = 0.6

        # Find the preamble
        start_inx = np.argmax(diff > (2-sensitivity)) # [0 0 0 0 1 0 0 0 1 0 1]

        if self._is_listening == True:
            voltages = in0[start_inx:] # Cut off the preamble
            voltages = voltages.reshape((-1, self.SPS)) # Create a matrix where each row represents a signle bit
            # Calculate the voltage averages and demodulate the data
            voltage_averages = np.average(voltages)
            voltage_averages = voltage_averages.reshape((1,-1))
            voltage_averages(voltage_averages > 0.25) = 1 
            # voltage_averages = [0.27 0.31 -0.33 -0.27 0.1 -0.7]
            voltage_averages(voltage_averages < -0.25) = 0
            self._num_of_noise_samples += sum(np.abs(voltage_averages) < 0.25) 
            if self._num_of_noise_samples > self._num_of_noise_samples_threshold:
                self._is_listening = False
                self._num_of_noise_samples = 0
            
            



# [1 1 -1] -> 0.3
# [1 -1 -1] -> -0.3
# avg with only noise~0

# 0.6 diff

# self.preamble_length = int(fs*t)
# self.SPS = int(3*fs*t)


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









        # for amplitude_index, amplitude in enumerate(diff):
        #     if amplitude == self._sens:

        #     current = diff[amplitude_index, amplitude_index + self._SPS]
        #     if amplitude_index + a.index(-1*self._sens) == self._fs*self._t:
        #         np.append(demodulated_data, 0)
        #         current_waiting_time = 0
        #         amplitude_index += a.index(-1*self._sens)
        #     elif amplitude_index + a.index(-1*self._sens) == 2*self._fs*self._t:
        #         np.append(demodulated_data, 1)
        #         current_waiting_time = 0
        #         amplitude_index += a.index(-1*self._sens)
        #     else:
        #         waiting_time += 1/self._fs
                

        # return len(input_items[0])


