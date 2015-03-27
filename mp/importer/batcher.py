# this function is intentionally get empty for now
# this program takes an iterable and splits in a number of batches using context arguments
# result of the run_in_batches is that each batch element is yielded and passed to the process_one function 

from itertools import *
from itertools import count

def get_batches(context, iterable, nb):
    bsize = context.batch_size
    startbatch = context.start_batch
    start = startbatch*bsize
    count = bsize*nb
    if nb == 0:		
        for i in iterable:
            count +=1
            if start+bsize*nb <= count-1 <= start+bsize*nb+bsize:      	# filter for yielding - in this loop i skip the first batch of size "start" = startbatch*bsize
                if count == start+bsize*nb+bsize:
                    yield i
                else:
                    yield i 
            else:
                continue           
    else:
        for i in iterable:
            count +=1
            if bsize*nb <= count-1 <= bsize*nb+bsize:      	
                if count == bsize*nb+bsize:
                    yield i
                else:
                    yield i 
            else:
                continue

def run_in_batches(context, iterable, end_batch):
    bmax = context.max_batches
    for nbatch in range(0,bmax):
        c = 0 
        got_batch = get_batches(context, iterable, nbatch)		
        for k in got_batch:
            c = c+1							 					
            yield k							
            if c < context.batch_size: 
                continue						
            elif c == context.batch_size:
                end_batch()						
                break                     
            # add if-else loop to end_batch() if batch is incomplete (it would be the last batch), now is in the test funcion
       

     
