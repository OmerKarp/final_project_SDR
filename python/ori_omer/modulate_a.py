#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2026 omer_karp.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
from collections import deque

class modulate_a(gr.sync_block):
    """
    docstring for block modulate_a
    t is in seconds
    """
    def __init__(self, t=1,fs=1000,msg="hi ori"):
        gr.sync_block.__init__(self,
            name="modulate_a",
            in_sig=None,
            out_sig=[np.float32])
        self._t=t
        self._fs=fs
        self._msg=msg

        self._SPS = int(3*fs*t)        # <number of samples per second> * <time that a 1/3 symbol is transmitted>
        self._preabmle_number_of_samples = int(fs*t)   # the preabmle is only t and not 3t time units

        self._queue = deque()
        # print("self queue = ", self._queue)

        self._modulated_zero = np.concatenate((np.ones(int(self._SPS/3)), -1*np.ones(int(self._SPS * 2/3))))
        self._modulated_one = np.concatenate((np.ones(int(self._SPS * 2/3)), -1*np.ones(int(self._SPS/3))))
        self._preamble = -10*np.ones(int(self._preabmle_number_of_samples))
        # print("0 -> ", self._modulated_zero, "size = ", np.size(self._modulated_zero))
        # print("1 -> ", self._modulated_one, "size = ", np.size(self._modulated_one))
        # print("preamble ->", self._preamble, "size = ", np.size(self._preamble))

        self.enqueue_from_string()
        # print("self queue = ", self._queue)

    def work(self, input_items, output_items):
        out = output_items[0]

        modulated_msg_chunk = np.zeros(len(out))

        if len(self._queue) > 0:
            for i in range(min(len(out), len(self._queue))):
                modulated_msg_chunk[i] = self._queue.popleft()
                # print(f"modulated_msg_chunk[until {i}] = ", modulated_msg_chunk)

        # print("modulated_msg_chunk -> ", modulated_msg_chunk)

        out[:] = modulated_msg_chunk
        return len(output_items[0])
    
    def enqueue_from_string(self):
        modulated_msg = np.zeros(self._SPS * 8 * len(self._msg)) # samples_per_symbol (symbol=bit) * number_of_bits_in_char * number_of_chars
        # print("modulated_msg -> ", np.size(modulated_msg))
        binary_msg = ''.join(format(ord(char), '08b') for char in self._msg)
        # print("binary_msg ->", binary_msg)
        for bit_index, bit in enumerate(binary_msg):
            # print("the bit is ", bit, type(bit))
            if bit == '0':
                modulated_msg[bit_index*self._SPS : (bit_index+1)*self._SPS] = self._modulated_zero
            else:
                modulated_msg[bit_index*self._SPS : (bit_index+1)*self._SPS] = self._modulated_one
            # print("from ", bit_index*self._SPS, " to ", (bit_index+1)*self._SPS, " we have ", modulated_msg[bit_index*self._SPS : (bit_index+1)*self._SPS])

        if len(self._queue) > 0:
            self._queue.extend(modulated_msg) # continue
        else:
            self._queue.extend(self._preamble) # also send the preabmle
            print("added a preamble!")
            self._queue.extend(modulated_msg)
