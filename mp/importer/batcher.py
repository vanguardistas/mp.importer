# this function is intentionally get empty for now
# this program takes an iterable and splits in a number of batches using context arguments
# result of the run_in_batches is that each batch element is yielded and passed to the process_one function 

from itertools import *
from itertools import count

def get_batches(context, iterable, nb):
    bsize = context.batch_size
    startbatch = context.start_batch
    start = startbatch*bsize
    count = 0
    for i in iterable:
        count +=1
        if start+bsize*nb <= count-1 <= start+bsize*nb+bsize:      	# skip the first batch of size "start" = startbatch*bsize
            yield i
        else:
            continue 

def run_in_batches(context, iterable, end_batch):
    bmax = context.max_batches
    c = 0
    for nbatch in range(0,bmax):					# TODO set default value, cannot be None
        got_batch = get_batches(context, iterable, nbatch)		# gets batch elements (yields) for each value of nbatch 
        for k in got_batch:	
            c = c+1							 											
            current_batch, position_in_batch = divmod(c, context.batch_size)
            current_batch += 1
            print ("current_batch, position_in_batch, k", current_batch, position_in_batch, k)			
            yield k
            if position_in_batch == 0:
                end_batch()
                break               

