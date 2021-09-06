# -*- coding: utf-8 -*-
"""
This example to show the use of the ni_daq_analog_in_out_module.py

Here we read analog samples from the channels defined under ai_channel_names,
with a defined sample rate and in blocks of size block_size.
Every iteration of the for loop below retrieves a block_size amount of samples.

The output writes waveforms that are synthesized by the dds functionality.
https://en.wikipedia.org/wiki/Direct_digital_synthesis
Given that the user wants to write a waveform, and he wants to write Ws many
waveforms per second. He gives the waveform with N points.
Ideally, Ws * N is equal to the sample rate. If Ws * N is an integer multiple
of the sample rate we can simply skip each time one or a few datapoints.
If the Ws * N / sample_rate is not an integer we can use interpolation on the
fly (which is resource consuming) or stick to the nearest datapoint.

@author: De Voogd Scientific
"""
import ni_daq_analog_in_out_module as aio
import json
import time
import numpy as np



#Some parameters
ai_channel_names = "Dev2/ai0:15"
sample_rate = 1000
block_size = 1
ao_channel_names = "Dev3/ao0:7"


#Initialize the hardware
settings = {} # This dictionary contains the settings and derived parameters throughout the setup
daq_in = aio.daq_reader(ai_channel_names, sample_rate, block_size = block_size)
settings["ai"] = next(daq_in)

daq_out = aio.daq_writer(ao_channel_names,settings["ai"]["sample rate"])
settings["ao"] = next(daq_out)


# DDS
Ws = 100         # waveforms per second.
N = 1000       # number of points in our arbitrary waveform.
waveform = np.array([np.sin(2*np.pi*x/N) for x in range(N)])
dds = aio.dat_out_gen(waveform, Ws, settings["ao"]["sample rate"])
settings["dds"] = next(dds)

#print settings after initialization in a pretty way
print('settings =', json.dumps(dict(settings),sort_keys=False, indent=4))


counter = 0
timezero = time.perf_counter()
# Run the hardware. The actual work is done in the two lines below
for data_in in daq_in:                      # This line calls next(daq_in), which is the same expression as daq_in.__next__() or daq_in.send(None), every iteration (as this is how for-loops in python are defined). The daq_in generator blocks untill enough ai samples are available in the hardware buffer. Hence, daq_in controls the timing.
    data_out1 = dds.send(np.shape(data_in)[1])      # ask for the same amount of samples as with data_in
    data_out = np.repeat([data_out1,],8,0)  # must be of size (#output_channels, blocksize) so (8,10)
    daq_out.send(data_out)            # This line lets the daq_out coroutine transfer the data_in to the hardware output buffer. daq_out returns immediately after the transfer, so it does NOT wait untill the samples our actually written on the analog output. 
    
    # below just some bookkeeping to see the time (in ms) every 100 iterations.
    counter+=1
    if counter%100==0:
        print('time: ', round((time.perf_counter()-timezero)*sample_rate/block_size), ' counter: ', counter)