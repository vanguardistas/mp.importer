# this function is intentionally get empty for now
# this program takes an iterable and splits in a number of batches using context arguments
# result is a list that contains the batches (for now) - TODO pass iterator

from itertools import *
from itertools import count

def run_in_batches(context, iterable, process_one): 		
    batch_size = context.batch_size
    start_batch = context.start_batch
    max_batches = context.max_batches
    start = start_batch*batch_size 
    tot_result = []
    for x in range (0,max_batches-1):											# for each batch creates a different list					
        my_iterator = islice(iterable, start+x*batch_size, start+x*batch_size+batch_size, 1)				
        batch = list(my_iterator)
        result = process_one(batch)
        if len(result) != 0:
            tot_result.append(result)
    return tot_result													# TODO  pass directly the iterator

# check what happens with max_batches (if they will be set by default on 100 for example)  -  avoid creating empty batches
# if I return an iterator, the assertion would change and so the process_one




