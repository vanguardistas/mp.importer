# -*- coding: utf-8 -*-
""" Create batches of elements from and iterable

This module contains utilities for creating batches of elements from an iterable
The user can select the batch size, the maximum number of batches and the starting batch for yielding elements
Other function will be added to randomly sample elements and to retrieve the last batch  
"""

def run_in_batches(iterable, end_batch_callback=None, batch_size=2, batch_start=0, max_batches=None):	
    """ Create batches from an iterable
   
    This function is a generator that creates batches of elements from an iterable 
    The callback function is called when a) maximum batches are reached or b) iterable is exhausted 
    All batches (complete and incomplete) are ended by a callback function
    """ 	
    c = 0
    ended = False
    for k in iterable:
        c = c + 1			
        current_batch, position_in_batch = divmod(c, batch_size)
        if position_in_batch == 0:
            current_batch = current_batch - 1						# last element of a batch has position=0, value=current_batch+1
        if current_batch >= batch_start and (max_batches is None or current_batch < batch_start + max_batches):
            ended = False
            yield k 
            if position_in_batch == 0: 							# ends completed batches
                end_batch_callback()
                ended = True
        if max_batches is not None and current_batch == batch_start + max_batches:	# if gets maximum allowed batches, break 
            break
    if ended is False:
        end_batch_callback()	


def parse_arguments(args=None):		 						# receives a list of all the arguments and create a parser with only batcher args	
    """ Parse arguments from user									 

    This function parses user input and returns the object args that contains arguments
    """
    import argparse
    parser = argparse.ArgumentParser(description='Pass arguments to batcher')				
    parser.add_argument('--argument_1', dest='batcher_argument_1', type=int, help="1st argument")
    parser.add_argument('--argument_2', dest='batcher_argument_2', type=int, help="2nd argument")
    options = None
    if args is not None: 
        options = parser.parse_args(args)						# need to skip the first argument (script name) if this function receives full args (args[:1])
    return options			 

def get_batcher_args(options):									
    """ Takes options and passes arguments to batcher

    Gets arguments parsed by parse_arguments to be passed as  a dictionary of keywords (**kw) to run_in_batches
    e.g. run_in_batches(iterable, end_batch, **get_batcher_args(options))
    """ 
    kw = dict()
    if options.batcher_argument_1:								# options object result of parse_args
        kw['batcher_argument_1'] = options.batcher_argument_1
    if options.batcher_argument_2:
        kw['batcher_argument_2'] = options.batcher_argument_2
    return kw										# dictionary of **wk for batcher, e.g. {'argument_1':10, 'argument_2':20}







