#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2026 omer_karp.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

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
        self._SPS = 3*fs*t        # <number of samples per second> * <time that a 1/3 symbol is transmitted>
        self._preabmle_number_of_samples = fs*t   # the preabmle is only t and not 3t time units


    def work(self, input_items, output_items):
        out = output_items[0]

        modulated_zero = np.concatenate(np.ones([1,self._SPS/3]), -1*np.ones([1,self._SPS * 2/3]))
        modulated_one = np.concatenate(np.ones([1,self._SPS * 2/3]), -1*np.ones([1,self._SPS/3]))
        preamble = -1*np.ones([1, self._preabmle_number_of_samples])

        modulated_msg = np.zeros([1, self._SPS * 8 * len(self._msg)]) # samples_per_symbol (symbol=bit) * number_of_bits_in_char * number_of_chars
        binary_msg = ''.join(format(ord(char), '08b') for char in self._msg)
        for bit_index, bit in enumerate(binary_msg):
            if bit == 0:
                modulated_msg[bit_index:bit_index+self._SPS] = modulated_zero
            else:
                modulated_msg[bit_index:bit_index+self._SPS] = modulated_one

        out[:] = np.concatenate(preamble, modulated_msg)
        return len(output_items[0])
