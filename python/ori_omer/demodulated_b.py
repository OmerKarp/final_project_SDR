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
from scipy import signal
from scipy.signal import find_peaks

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
        self._preamble_number_of_samples = int(t*fs)
        self._preamble_voltages = -1 * np.ones(self._preamble_number_of_samples)

        self._num_of_noise_bits = 0
        self._is_listening = False
        self._num_of_noise_bits_threshold = int(np.ceil(fs*timeout_seconds / self._SPS)) # number_of_noise_samples_needed / number_of_samples_in_a_bit

        self._decoded_bits = deque()
        self._samples_buffer = np.zeros(self._SPS) # [1 -1 0 0 0 0 0]
        self._samples_buffer_last_index = 0        #       +2

    def work(self, input_items, output_items):
        in0 = input_items[0]
        print("(+) in0 length", len(in0))
        if not self.is_input_size_valid(in0):
            print("(-) ERROR: input length is less than 1", len(in0))
            return len(input_items[0])

        # If not listening, search for the preabmle
        if not self._is_listening:
            # we chache the data until we have more than fs*t samples to do correlation with
            samples = self.update_buffer_with_preamble(in0)
            if len(samples) == 0:
                # print(f"(-) Waiting for more samples for doing correlation, {self._samples_buffer_last_index} / {int(self._t * self._fs)}")
                return len(input_items[0])

            preable_end_index = self.find_preabmle(samples)
            if preable_end_index == -1:
                return len(input_items[0])
            
            self._is_listening = True
            self._samples_buffer_last_index = 0 # don't need to store preamble parts anymore
            in0 = samples[preable_end_index+1:]

        # If listening, precess the data until only noise is found for timeout_seconds
        if self._is_listening:
            working_samples = self.use_and_update_samples_buffer(in0)
            
            if len(working_samples) == 0: # if all the samples went to the buffer, don't process
                # print(f"(-) We need more samples for a bit, {self._samples_buffer_last_index} / {self._SPS}")
                return len(input_items[0])
            
            demodulated_msg, number_of_noisy_bits = self.convert_samples_to_bits(working_samples)

            # handle noise count
            self.update_noise_count(number_of_noisy_bits)

            # add the decoded bits to a queue
            self._decoded_bits.extend(demodulated_msg.astype(int))

            # use the queue to print chars
            self.print_chars_from_queue()
            
            return len(input_items[0])
        
    ######################## HELPER FUNCTIONS ########################

    def is_input_size_valid(self, in0):
        """
        checks if the size of the in0 is bigger than 1
        """
        if len(in0) < 1:
            return False
        return True
    
    def update_buffer_with_preamble(self, in0):
        samples = np.concatenate((self._samples_buffer[0:self._samples_buffer_last_index], in0)) # adds the old buffer to the start
        total_number_of_samples = len(samples)

        if total_number_of_samples >= self._preamble_number_of_samples:
            self._samples_buffer_last_index = self._preamble_number_of_samples      # full size
            self._samples_buffer[0 : self._samples_buffer_last_index] = samples[-self._preamble_number_of_samples:]   # save the last X samples, that X is the size of the preamble
        else:
            # append to the buffer the new samples
            self._samples_buffer_last_index = len(samples)
            self._samples_buffer[0 : self._samples_buffer_last_index] = samples
            return np.array([])
        
        return samples

    def find_preabmle(self, in0):
        """
        finds the preabmle using correlation
        """
        corr = signal.correlate(in0, self._preamble_voltages)
        corr = np.round(corr, 2)
        print("corr", corr)

        max_possible_corr = self._fs * self._t
        threshold = max_possible_corr * self._sens

        peaks, _ = find_peaks(corr, distance=self._SPS/2, height=threshold)

        # check if there was acually a preamble
        if len(peaks) == 0:
            print("(-) Only Noise was found")
            return -1

        preamble_end_index = peaks[0]
        print("(+) Preable was found with max corr = ", corr[preamble_end_index], " at index = ", preamble_end_index)
        return preamble_end_index

    def use_and_update_samples_buffer(self, in0):
        """
        use the in-memory buffer to get old leftover samples and cache the new leftover samples
        """
        full_data = np.concatenate((self._samples_buffer[0:self._samples_buffer_last_index], in0)) # adds the old buffer to the start

        save_samples_to_buffer_index = np.mod(len(full_data), self._SPS)
        working_samples_index = len(full_data) - save_samples_to_buffer_index

        add_to_buffer_samples = full_data[working_samples_index:]
        working_samples = full_data[0:working_samples_index]
        
        # update the buffer to the new samples to store
        self._samples_buffer_last_index = save_samples_to_buffer_index
        self._samples_buffer[0 : save_samples_to_buffer_index] = add_to_buffer_samples

        return working_samples
    
    def convert_samples_to_bits(self, working_samples):
        """
        process the samples and convert them to bits
        """
        # Create a matrix where each row represents a signle bit
        voltages = working_samples.reshape((-1, self._SPS))

        # Calculate the voltage averages and demodulate the data
        voltage_averages = np.average(voltages, axis=1)
        print("(+) voltage_averages = ", voltage_averages)

        null_value = -1
        demodulated_msg = null_value*np.ones(np.size(voltage_averages))

        detected_bit_threshold = 0.1
        # example: voltage_averages = [0.27 0.31 -0.33 -0.27 0.1 -0.7]
        one_indexes = np.array(voltage_averages > detected_bit_threshold)           # [0 1 0 0 0]
        zero_indexes = np.array(voltage_averages < -detected_bit_threshold)         # [1 0 0 0 0]
        noise_indexes = np.array(np.abs(voltage_averages) < detected_bit_threshold) # [0 0 1 1 1]

        # should set the 1's and 0's, and the noise should stay at -1, example: [0 1 1 0 0 1 0 -1 -1 -1 -1 -1 -1]
        demodulated_msg[one_indexes] = 1
        demodulated_msg[zero_indexes] = 0

        start_of_noise_index = np.argmax(noise_indexes)                                 # get the first index of noise
        if np.abs(voltage_averages[start_of_noise_index]) < detected_bit_threshold:     # check if we really found noise
            print("the noise starts at index = ", start_of_noise_index)
            demodulated_msg = demodulated_msg[:start_of_noise_index]
            # now we don't have the -1's, example: example: [0 1 1 0 0 1 0]
        
        number_of_noisy_bits = sum(noise_indexes)
        return demodulated_msg, number_of_noisy_bits

    def update_noise_count(self, number_of_noisy_bits):
        """
        hanldes all checks and counts for noise in the system, and responsible for stop listening
        """
        self._num_of_noise_bits += number_of_noisy_bits

        if self._num_of_noise_bits >= 1:
            print(f"(+) Current noisy bits, from threshold = {self._num_of_noise_bits} / {self._num_of_noise_bits_threshold}")

        # if we got noise for too long, we stop listening and start again searching for preamble
        if self._num_of_noise_bits >= self._num_of_noise_bits_threshold:
            self._is_listening = False
            self._num_of_noise_bits = 0

    def print_chars_from_queue(self):
        """
        prints chars as long as there are more than 8 bits in the bits queue
        """
        while len(self._decoded_bits) >= 8:
            x = np.zeros(8, dtype=int)
            for i in range(8):
                x[i] = int(self._decoded_bits.popleft())
            # print("x -> ", x)

            binary_str =''.join(map(str,x))
            # print("binary_str = ", binary_str, "int(binary_str) = ", int(binary_str, 2))
            print(chr(int(binary_str, 2)))
