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
        if start+bsize*nb <= count-1 <= start++bsize*nb+bsize-1:     # for now takes only the first batch 
            yield i

def run_in_batches(context, iterable, process_one):
    bmax = context.max_batches
    tot_result = []
    for nbatch in range(0,bmax):				      # for each batch launches the pipeline (get-batches and process)
        got_batch = get_batches(context, iterable, nbatch)
        for k in got_batch:
       	    result = process_one(k)					# tot_result.append(result) - instead of nesting lists, merge
            tot_result += result
            #yield k							# yield for statistics function (in pipeline)? TODO
        end_batch(context,nbatch)					
    return tot_result

#TODO: add to session #context.sess.add(result) or it will be done out of this function?

# call the end_batch function when each batch is over
def end_batch(context, nb):
    pass
    #print "end batch number", nb
    #context.sess.flush()

# yield got_batch.next()
def statistics(context,got_batch):
   ok = 0
   not_ok = 0
   for k in got_batch:
       if k is not None:
           ok = ok+1
       else:
           not_ok = not_ok+1
   #context.prob() # "problems for this batch are", not_ok



