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
    """
    def __init__(self, t=1,fs=1000,msg="hi ori"):
        gr.sync_block.__init__(self,
            name="modulate_a",
            in_sig=None,
            out_sig=[np.complex64])
        self._t=t
        self._fs=fs
        self._msg=msg
        self._SPS = 3 * fs/t        # <number of samples per second> / <time that a 1/3 symbol is transmitted>
        self._preabmle_SPS = fs/t   # the preabmle is only t and not 3t time units


    def work(self, input_items, output_items):
        out = output_items[0]
        for letter in self._msg:
            

        # <+signal processing here+>
        out[:] = whatever
        return len(output_items[0])
