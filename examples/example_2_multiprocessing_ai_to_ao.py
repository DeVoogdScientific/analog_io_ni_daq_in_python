# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 22:19:48 2021

@author: devoo
"""
import multiprocessing as mp
import json
import ni_daq_analog_in_out_module as aio
    
def hardware_loop(settings: dict):
    """
    This function is run in a different process for optimal stability and speed.
    It handles all the hardware communication with the NI DAQ. This function
    does the same as example_1, however it cannot print anything, so the counter
    is written into a shared dictionary.

    Parameters
    ----------
    settings : proxy dict
        shared dictionary with information about hardware settings, status,
        and it holds the stop flag.

    """
    #Some parameters
    ai_channel_names = "Dev2/ai0:15"
    sample_rate = 10000
    block_size = 10
    ao_channel_names = "Dev3/ao0:7"
    
    #Initialize the hardware
    daq_in = aio.daq_reader(ai_channel_names, sample_rate, block_size = block_size)
    settings["ai"] = next(daq_in)
    
    daq_out = aio.daq_writer(ao_channel_names,settings["ai"]["sample rate"])
    settings["ao"] = next(daq_out)
    
    settings["counter"] = 0
    # Run the hardware. The actual work is done in the two lines below
    for data_in in daq_in:                  # This line calls next(daq_in), which is the same expression as daq_in.__next__() or daq_in.send(None), every iteration (as this is how for-loops in python are defined). The daq_in generator blocks untill enough ai samples are available in the hardware buffer. Hence, daq_in controls the timing.
        daq_out.send(data_in[0:8,:])        # This line lets the daq_out coroutine transfer the data_in to the hardware output buffer. daq_out returns immediately after the transfer, so it does NOT wait untill the samples our actually written on the analog output. 
        if settings['stop']:
            break
        settings["counter"]+=1
    return
        
def user_io_loop(settings: dict):
    """
    This function is run on the main process as it interacts with the user.
    It asks for some command and it executes the proper task if the input
    was recgonized.

    Parameters
    ----------
    settings : proxy dict
        shared dictionary with information about hardware settings, status,
        and it holds the stop flag.

    Returns
    -------
    settings : dict
        Returns a copy of the proxy dict 'settings'. The copy is made after
        the stop signal is flagged.

    """
    print('Started analog in/out')
    while not settings['stop']:
        inp = input('analog i/o prompt >>>> ')
        if inp == 'q' or inp == 'quit' or inp == 'stop':
            settings['stop'] = True
        elif inp == 's' or inp == 'settings':
            print('settings =', json.dumps(dict(settings),sort_keys=False, indent=4))
        else:
            print('Input "', inp, '" is not recognized.', sep = '')
    return dict(settings)


# MAIN PROGRAM    
def main():
    with mp.Manager() as manager:
        settings = manager.dict()
        settings['stop'] = False
        hl = mp.Process(target=hardware_loop, args=[settings])
        hl.start()
        settings_final = user_io_loop(settings)
        hl.join()
    print(json.dumps(settings_final,sort_keys=False, indent=4))
    return

if __name__ == '__main__':
    main()