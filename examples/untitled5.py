# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 15:03:08 2021

@author: lion
"""
import numpy as np


def dat_out_gen(waveform, waveform_rate, sample_rate):
    """
    Generator function for creating samples from predefined waveform.

    Parameters
    ----------
    waveform : np.array
        Array holding the waveform
    waveform_rate : number
        Specifies the needed numbers of waveforms to output in waveforms/s
    sample_rate : integer
        The analog output sample rate that is set.

    Yields
    ------
    Yield in: n: int
        Send in the needed number of samples
    yield out: piece of waveform: np.array
        Gives a numpy array with the following n values for analog output.

    """
    N = len(waveform)
    skip_factor = waveform_rate*N/sample_rate
    i = 0 
    n = yield
    while True:
        ind = ( ((np.arange(n)+i)*skip_factor) % N ).astype(int)
        i+=n # To fix in future: a step might occur when this number overflows
        n = yield waveform[ind]


N = 10
waveform = np.array([np.sin(2*np.pi*x/N) for x in range(N)])  

do = dat_out_gen(waveform, 10, 100)
next(do)
dat_out = do.send(40)
[print(dat_out[i]) for i in range(len(dat_out))]
dat_out = do.send(40)
[print(dat_out[i]) for i in range(len(dat_out))]
dat_out = do.send(40)
[print(dat_out[i]) for i in range(len(dat_out))]
dat_out = do.send(40)
[print(dat_out[i]) for i in range(len(dat_out))]
dat_out = do.send(40)
[print(dat_out[i]) for i in range(len(dat_out))]
dat_out = do.send(40)
[print(dat_out[i]) for i in range(len(dat_out))]
dat_out = do.send(40)
[print(dat_out[i]) for i in range(len(dat_out))]
