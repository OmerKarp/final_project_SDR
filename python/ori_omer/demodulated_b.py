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

        self._SPS = int(3*fs*t)     # <number of samples per second> * <time that a 1/3 symbol is transmitted>

        self._num_of_noise_samples = 0
        self._is_listening = False
        self._num_of_noise_samples_threshold = fs*timeout_seconds

        self._decoded_bits = deque()
        # print("initialized demod block!")
        self._samples_buffer = np.zeros(self._SPS) # [1 -1 0 0 0 0 0]
        self._samples_buffer_last_index = 0        #       +2

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
                return len(input_items[0])

        if self._is_listening: # listening!
            print("SPS = ", self._SPS)  # SPS = 3000
            print("in0 and its size -> ", in0, np.size(in0))    # we want to split it from 8192 -> 6000 (SPS*2) , and save 2192 in a buffer for later

            full_data = np.concatenate((self._samples_buffer[0:self._samples_buffer_last_index], in0)) # add the bits from the buffer, they are the last samples before -> first samples now
            print("full data and its size -> ", full_data, np.size(full_data))

            save_samples_to_buffer_index = np.mod(len(full_data), self._SPS)            # 2192
            working_samples_index = len(full_data) - save_samples_to_buffer_index  # 6000
            print("save_samples_to_buffer_index -> ", save_samples_to_buffer_index)
            print("working_samples_index -> ", working_samples_index)

            add_to_buffer_samples = full_data[working_samples_index:]
            working_samples = full_data[0:working_samples_index]
            print("add_to_buffer_samples -> ", add_to_buffer_samples, len(add_to_buffer_samples))
            print("working_samples -> ", working_samples, len(working_samples))

            # add the samples to the buffer
            self._samples_buffer_last_index = save_samples_to_buffer_index
            self._samples_buffer[0 : save_samples_to_buffer_index] = add_to_buffer_samples
            print("_samples_buffer_last_index", self._samples_buffer_last_index)
            print("_samples_buffer", self._samples_buffer, len(self._samples_buffer))

            # in0 = np.concatenate((in0, np.zeros(np.mod(self._SPS - len(in0), self._SPS))))

            # [1 2 3 4 5 6] ->
            # [1 2 3
            #  4 5 6]
            voltages = working_samples.reshape((-1, self._SPS)) # Create a matrix where each row represents a signle bit
            # print("voltage_averages = ", voltages)
            # print(np.unique(voltages[0,:], return_counts=True))
            # print(np.unique(voltages, return_counts=True))
            # print(np.unique(voltages, return_counts=True, axis=0))

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
            one_indexes = np.array(voltage_averages > 0.25)           # [0 1 0 0 0]
            zero_indexes = np.array(voltage_averages < -0.25)         # [1 0 0 0 0]
            noise_indexes = np.array(np.abs(voltage_averages) < 0.25) # [0 0 1 1 1]
            print("one_indexes = ", one_indexes)
            print("zero_indexes = ", zero_indexes)
            demodulated_msg[one_indexes] = 1
            demodulated_msg[zero_indexes] = 0
            print("demodulated_msg -> ", demodulated_msg) # [0 1 1 0 0 1 0 -1 -1 -1 -1 -1 -1]

            start_of_noise_index = np.argmax(noise_indexes)           # get the first index of noise
            if np.abs(voltage_averages[start_of_noise_index]) < 0.25: # check if we really found noise
                # there is noise...
                print("the noise starts at index = ", start_of_noise_index)
                demodulated_msg = demodulated_msg[:start_of_noise_index] # $ look if we need to fix
                print("demodulated_msg -> ", demodulated_msg)

            # now we check how many noise samples we got $ look if we need to fix
            self._num_of_noise_samples += sum(noise_indexes) 
            if self._num_of_noise_samples > self._num_of_noise_samples_threshold:
                self._is_listening = False
                self._num_of_noise_samples = 0

            self._decoded_bits.extend(demodulated_msg.astype(int)) # add the decoded bits to a queue
            print("new queue ->", self._decoded_bits)
            while len(self._decoded_bits) >= 8:        # prints a char if there are more than 8 bits in the queue
                x = np.zeros(8, dtype=int)
                for i in range(8):
                    x[i] = int(self._decoded_bits.popleft())
                print("x -> ", x)

                binary_str =''.join(map(str,x))
                # print("binary_str = ", binary_str, "int(binary_str) = ", int(binary_str, 2))
                print(chr(int(binary_str, 2)))
            
            return len(input_items[0])