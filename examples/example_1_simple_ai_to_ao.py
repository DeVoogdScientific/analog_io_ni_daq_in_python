# -*- coding: utf-8 -*-
"""
Simple example to show the use of the ni_daq_analog_in_out_module.py

Here we read analog samples from the channels defined under ai_channel_names,
with a defined sample rate and in blocks of size block_size.
Every iteration of the for loop below retrieves a block_size amount of samples
and writes this data in the same loop back to the analog output.
The delay between ai and ao is ideally thus only block_size/sample_rate seconds.

@author: De Voogd Scientific
"""
import ni_daq_analog_in_out_module as aio
import json
import time

#Some parameters
ai_channel_names = "Dev2/ai0:15"
sample_rate = 10000
block_size = 10
ao_channel_names = "Dev3/ao0:7"

#Initialize the hardware
settings = {} # This dictionary contains the settings and derived parameters throughout the setup
daq_in = aio.daq_reader(ai_channel_names, sample_rate, block_size = block_size)
settings["ai"] = next(daq_in)

daq_out = aio.daq_writer(ao_channel_names,settings["ai"]["sample rate"])
settings["ao"] = next(daq_out)
 
#print settings after initialization in a pretty way
print('settings =', json.dumps(dict(settings),sort_keys=False, indent=4))


counter = 0
timezero = time.perf_counter()
# Run the hardware. The actual work is done in the two lines below
for data_in in daq_in:                  # This line calls next(daq_in), which is the same expression as daq_in.__next__() or daq_in.send(None), every iteration (as this is how for-loops in python are defined). The daq_in generator blocks untill enough ai samples are available in the hardware buffer. Hence, daq_in controls the timing.
    daq_out.send(data_in[0:8,:])        # This line lets the daq_out coroutine transfer the data_in to the hardware output buffer. daq_out returns immediately after the transfer, so it does NOT wait untill the samples our actually written on the analog output. 
    
    # below just some bookkeeping to see the time (in ms) every 100 iterations.
    counter+=1
    if counter%100==0:
        print('time: ', round((time.perf_counter()-timezero)*sample_rate/block_size), ' counter: ', counter)