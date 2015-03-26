# this function is intentionally get empty for now
# this program takes an iterable and splits in a number of batches using context arguments
# result of the run_in_batches is that each batch element is yielded and passed to the process_one function 

from itertools import *
from itertools import count

def get_batches(context, iterable, nb):
    count = 0
    bsize = context.batch_size
    ssize = context.start_batch
    start = ssize*bsize
    for i in iterable:
        count += 1
        if start+bsize*nb <= count-1 <= start+bsize*nb+bsize-1:      	# filter for yielding - takes the nb-batch 
            print ("batch", i)
            yield i


def run_in_batches(context, iterable, end_batch):
    bmax = context.max_batches
    for nbatch in range(0,bmax):
        print ('nbatch', nbatch)
        got_batch = get_batches(context, iterable, nbatch)		# gets batch elements (yields) for each value of nbatch
        c = 0 
        nbatch = nbatch+1
        for k in got_batch:
            c = c+1						# in the yielded batch, appends X in the right place
            yield k
            if c == context.batch_size:
                end_batch()						        # appends 'X' when batch ends


