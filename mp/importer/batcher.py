# -*- coding: utf-8 -*-
""" This module contains utilities for creating batches of elements from an iterable, in order to import them"""

def run_in_batches(iterable, end_batch_callback=None, batch_size=2, batch_start=0, max_batches=None):	
    """ This function is a generator that creates batches of elements from an iterable. 
        The callback function is called when a) maximum batches are reached or b) iterable is exhausted, also for incomplete batches 
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
        if max_batches is not None and current_batch == batch_start + max_batches:					# if gets maximum allowed batches, break 
            break
    if ended is False:
        end_batch_callback()	


