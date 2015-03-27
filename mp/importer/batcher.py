# this function is intentionally get empty for now
# this program takes an iterable and splits in a number of batches using context arguments
# result of the run_in_batches is that each batch element is yielded and passed to the process_one function 

from itertools import *
from itertools import count

def get_batches(context, iterable, nb):
    bsize = context.batch_size
    ssize = context.start_batch
    start = ssize*bsize
    count = start+bsize*nb						# every time the counter must be set in order to retrieve the correct batch and for the generator to be looped consecutively
    for i in iterable:
        count += 1
        if start+bsize*nb <= count-1 <= start+bsize*nb+bsize:      	# filter for yielding - takes the nb-batch 
            if count == start+bsize*nb+bsize:
                print ("LAST batch element", i)
                yield i
            else:
                print ("batch element", i)
                yield i            

def run_in_batches(context, iterable, end_batch):
    bmax = context.max_batches
    for nbatch in range(0,bmax):
        c = 0 
        print ('nbatch', nbatch)
        got_batch = get_batches(context, iterable, nbatch)		# gets batch elements (yields) for each value of nbatch - changes at every iteration
        for k in got_batch:
            c = c+1							# counter 					
            print (c, k)
            yield k							# in the yielded batch, appends X in the right place
            if c < context.batch_size:
                continue						
            else:
                end_batch()						# appends 'X' when batch ends
                break


