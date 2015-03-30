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
    for nbatch in range(0,bmax):					# TODO change according to Brian suggestion
        c = 0 
        got_batch = get_batches(context, iterable, nbatch)		# gets batch elements (yields) for each value of nbatch 
        for k in got_batch:
            c = c+1							 					
            yield k							
            if c < context.batch_size: 
                continue						
            elif c == context.batch_size:
                end_batch()						
                break         

                
# hmm, I wonder why we are iterating over the batches, surely it is simpler to just iterate over the iterator directly?
# There's this wonderful formula you can use:

#current_batch, position_in_batch = divmod(count_of_total_items_iterated_over, batch_size)
#current_batch += 1 # first batch is 1, but dived gives us zero
#if position_in_batch == 0:
    #end_batch()
