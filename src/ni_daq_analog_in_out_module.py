# -*- coding: utf-8 -*-
"""
Module to use NI DAQ analog input and analog output in python

This module provides functions to capture and write analog signals 
from National Instruments DAQ cards. We avoid the use of classes
in this module, so the functions are easy to copy and alter for
different use cases. Instead we use generator and coroutine like
functions, see explanation for this type of functions:
    https://www.geeksforgeeks.org/generators-in-python/
    https://www.geeksforgeeks.org/coroutine-in-python/
The first call of the generator/coroutine starts the communication
with the device and yields back information about the settings in 
a dictionary. Each call the first one that is to retrieve/send data. 

Check the examples in the examples folder!

@author: De Voogd Scientific
"""

import nidaqmx
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter
import numpy as np

def daq_reader(physical_channels: str, sample_rate: int, block_size: int = 1):
    """
    Generator-function that on first call will initialize a NI DAQ analog
    input card and on all later calls will return analog input data.
    
    Warning: This generator-function blocks untill enough samples are available!
    
    Parameters
    ----------
    physical_channels : str
        Specify the analog input channel(s), e.g. "Dev2/ai0:15".
    sample_rate : int
        The amount of samples this generator gives per second.
    block_size : int, optional
        The amount of samples this generator yields after each call. Hence this
        generator must on be called (with next(...)) on average faster than 
        each block_size/sample_rate timeinterval.
        The default is 1.

    Yields
    ------
    outputs yield 1: 
        yields dictionary with information about settings
    outputs yield 2+: 
        samples: an np.ndarray array of dimensions (#channels, block_size).
    """
    
    settings = { "physical channels"        : physical_channels,
                 "number of channels"       : len(nidaqmx._task_modules.channels.channel.Channel(0,physical_channels).channel_names),
                 "sample rate"              : sample_rate,
                 "sample block size"        : block_size
               }
    
    data_in = np.zeros( (settings["number of channels"],settings["sample block size"]) ,'d')
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(settings["physical channels"],terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
        task.in_stream.auto_start=0
        task.timing.cfg_samp_clk_timing(settings["sample rate"],
                                        source="OnboardClock", 
                                        sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                                        samps_per_chan=settings["sample rate"]*5) #let's set a buffer size that can hold 5 seconds of data
        reader = AnalogMultiChannelReader(task.in_stream)
        yield settings
        task.start()
        while True:
            reader.read_many_sample(data_in, number_of_samples_per_channel=settings["sample block size"])
            yield data_in



def daq_writer(physical_channels: str, sample_rate: int):
    """
    Coroutine-function that on first call will initialize a NI DAQ analog
    output card and on all later calls will send analog output data.
    
    Warning: This coroutine-function does NOT block untill all samples are
    written, but continues as soon as the samples are transferred to the 
    hardware output buffer!
    
    Parameters
    ----------
    physical_channels : str
        Specify the analog output channel(s), e.g. "Dev3/ao0:7".
    sample_rate : int
        The amount of samples this generator per second.

    Yields
    ------
    outputs yield 1:
        yields dictionary with information
    input yield 2+:
        data: an np.ndarray array of dimensions (#channels, sample block size (can be anything)).
    """
    settings = { "physical channels"        : physical_channels,
                 "number of channels"       : len(nidaqmx._task_modules.channels.channel.Channel(0,physical_channels).channel_names),
                 "sample rate"              : sample_rate
                }
    
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(settings["physical channels"])#check
        task.timing.cfg_samp_clk_timing(settings["sample rate"],
                                        source="OnboardClock", 
                                        sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                                        samps_per_chan=sample_rate*5) #let's set a buffer size that can hold 5 seconds of data
        writer = AnalogMultiChannelWriter(task.out_stream)
        yield settings
        data_out = (yield)
        task.start()
        while True:
            writer.write_many_sample(data_out)
            data_out = (yield)

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
    outputs yield: n: int
        yields dictionary with information
    outputs and inputs yield 2+: 
        send in: n: int
            needed number of samples
        outputs: piece of waveform: np.array
            Gives a numpy array with the following n values for analog output.

    """
    settings = {"waveform rate" : waveform_rate,            # in waveforms per second
                "sample rate"   : sample_rate,              # in samples per second
                "N"             : len(waveform),            # in numbers of samples
                "skip factor"   : waveform_rate*len(waveform)/sample_rate   # in fractional samples
                }
    i = 0 
    n = yield settings
    while True:
        ind = ( ((np.arange(n)+i)*settings["skip factor"]) % settings["N"] ).astype(int)
        i+=n # To fix in future: a step might occur when this number overflows
        n = yield waveform[ind]

if __name__ == "__main__":
    help(__name__)
        