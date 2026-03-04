#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2026 omer_ori.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import numpy as np
from gnuradio import gr

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

        self._SPS = int(3*fs*t)     # <number of samples per second> * <time that a 1/3 symbol is transmitted>

        self._num_of_noise_samples = 0
        self._is_listening = False
        self._num_of_noise_samples_threshold = fs*timeout_seconds
        print("initialized demod block!")

    def work(self, input_items, output_items):
        in0 = input_items[0]
        print(in0, np.size(in0))

        if not self._is_listening:
            # Find the preamble

            # [-1   1 1-1   1-1-1] -> [2 0 -2   2 -2 0]
            # 2 Represents the beginning of a bit, the location of -2 marks if it's 0 or 1
            # [2 -2 0] -> 0
            # [2 0 -2] -> 1
            diff = np.diff(in0)

            diff_above_threshold = diff > (2-self._sens) # [0 0 0 0 1 0 0 0 1 0 1]
            start_index = np.argmax(diff_above_threshold)

            # we need to check if the value in that start_index is acually valid
            # it can be invalid if we only got noise then diff_above_threshold = [0 0 0 ...]
            if diff[start_index] > (2-self._sens):
                # we indeed found a preample!
                print("the diff was", diff[start_index], ", index = ", start_index)
                self._is_listening = True
                in0 = in0[start_index+1:]

            else:
                print("no preample was found...")
                return len(input_items[0]) # $ IS THIS CORRECT? or "return 0"

        if self._is_listening: # listening!
            # padding 0's if needed for the reshape in the next step
            in0 = np.concatenate((in0, np.zeros(np.mod(self._SPS - len(in0), self._SPS))))
            print("SPS = ", self._SPS)
            print(in0, np.size(in0))

            # [1 2 3 4 5 6] ->
            # [1 2 3
            #  4 5 6]
            voltages = in0.reshape((-1, self._SPS)) # Create a matrix where each row represents a signle bit
            print("voltage_averages = ", voltages)
            print(np.unique(voltages[0,:], return_counts=True))
            print(np.unique(voltages, return_counts=True))
            print(np.unique(voltages, return_counts=True, axis=0))

            # Calculate the voltage averages and demodulate the data
            # [2 5]
            voltage_averages = np.average(voltages, axis=1)
            print("voltage_averages = ", voltage_averages)
            demodulated_msg = -1*np.ones(np.size(voltage_averages))
            print("demodulated_msg -> ", demodulated_msg)

            # [2 5]
            # voltage_averages = voltage_averages.reshape((1,-1))
            # print("voltage_averages = ", voltage_averages)

            # voltage_averages = [0.27 0.31 -0.33 -0.27 0.1 -0.7]
            one_indexes = (voltage_averages > 0.25)
            zero_indexes = (voltage_averages < -0.25)
            print("one_indexes = ", one_indexes)
            print("zero_indexes = ", zero_indexes)
            print("demodulated_msg[one_indexes] -> ", demodulated_msg[one_indexes])
            demodulated_msg[one_indexes] = 1
            demodulated_msg[zero_indexes] = 0

            # now we check how many noise samples we got
            self._num_of_noise_samples += sum(np.abs(voltage_averages) < 0.25) 
            if self._num_of_noise_samples > self._num_of_noise_samples_threshold:
                self._is_listening = False
                self._num_of_noise_samples = 0

            out_str = ""
            for i in range(0, len(demodulated_msg), 8):
                x = demodulated_msg[i, i+8]
                l=''.join([str(j) for j in x[::-1]])
                out_str += chr(int(("0b"+l), base=2))
            
            print(out_str)