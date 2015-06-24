# -*- coding: utf-8 -*-
""" Create batches of elements from and iterable

This module contains utilities for creating batches of elements from an iterable
The user can select the batch size, the maximum number of batches and the starting batch for yielding elements
Other function will be added to randomly sample elements and to retrieve the last batch  
"""
import random
import logging


def run_in_batches(iterable, end_batch_callback=None, batch_size=2, batch_start=0, max_batches=None, seed=None, percentage=None):	
    """ Create batches from an iterable
   
    This function is a generator that creates batches of elements from an iterable 
    The callback function is called when a) maximum batches are reached or b) iterable is exhausted 
    All batches (complete and incomplete) are ended by a callback function

    If random options are not None, gets a percentage of the total data (in range 0-100)
    The percentage value is converted to integer so it's an approximated value

    Pseudo-samples randomly the elements in the selected percentage (approximate)
    The main script logs the seed to make it repeatable (if seed not passed, uses current system time)
    """ 	
    c = 0
    ended = False
    if percentage is not None:
        mask = set([])										# create the mask without using random.sample
        random.seed(seed)									# seed can be passed as kw to be repeatable
        logging.info('SEED FOR THIS IMPORT: {}'.format(seed))    				# the function logs the seed value (if none, is generated here)				

        while len(mask) < int(((100-percentage)*batch_size)/100):
            i = int(random.random() * 10)							# *1000 perche bathc sono da 1000?
            if i == 0 or i in mask:
                continue
            mask.add(i)
    else:
        mask = None										
    for k in iterable:
        c = c + 1			
        current_batch, position_in_batch = divmod(c, batch_size)
        if mask is not None and position_in_batch in mask:					# yield only values that are not in the mask! 
            continue
        if position_in_batch == 0:
            current_batch = current_batch - 1							# last element of a batch has position=0, value=current_batch+1
        if current_batch >= batch_start and (max_batches is None or current_batch < batch_start + max_batches):
            ended = False
            yield k 
            if position_in_batch == 0: 								# ends completed batches
                if end_batch_callback is not None:
                    end_batch_callback()
                ended = True
        if max_batches is not None and current_batch == batch_start + max_batches:		# if gets maximum allowed batches, break 
            break
    if ended is False and end_batch_callback is not None:
        end_batch_callback()


def add_arguments(parser):		 						
    """ Adds batcher arguments to the parser									 

    This function gets the parser containing user inputs
    It adds arguments and returns a parser
    The parsing of args is performed in the main script 
    """ 
    parser.add_argument('--batch-size', dest='batch_size', action='store', default=1000, 
                       type=int, help="Number of elements in each batch")					
    parser.add_argument('--batch-start', dest='batch_start', action='store', default=0, 
                       type=int, help="starts importing batches from a given batch")
    parser.add_argument('--max-batches', dest='max_batches', action='store', default=None, 
                       type=int, help="Maximum amount of batches imported")
    parser.add_argument('--percentage', dest='percentage', action='store', default=None,	
                       type=int, help="Percentage of elements to be randomly sampled (0-100%)")	
    parser.add_argument('--seed', dest='seed', action='store', default=None, 
                       type=int, help="Seed to reproduce last imported batch")	


def get_batcher_args(options):									
    """ Takes namespace and filters batcher arguments

    Gets namespace with arguments parsed by parse_arguments 
    Filters only the batcher arguments 
    Stores arguments in a dictionary of keywords (**kw) for "run_in_batches"
    e.g. run_in_batches(iterable, end_batch, **get_batcher_args(options))
    """ 
    kw_temp = vars(options)
    kw = dict()											
    for i, j in kw_temp.items():							 
        if i not in ('batch_size', 'batch_start', 'max_batches', 'percentage', 'seed'):
            continue
        if j is None:
            continue        
        kw[i] = j										
    return kw										

