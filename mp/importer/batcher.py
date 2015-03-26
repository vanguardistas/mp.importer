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
        if start+bsize*nb <= count-1 <= start++bsize*nb+bsize-1:      	# for now takes only the first batch 
            yield i

def run_in_batches(context, iterable, process_one):
    bmax = context.max_batches
    tot_tot_result = []
    for nbatch in range(0,bmax):
        tot_result = []				     			# for each batch launches the pipeline (get-batches and process)
        got_batch = get_batches(context, iterable, nbatch)
        for k in got_batch:
       	    result = process_one(k)					# tot_result.append(result) - instead of nesting lists, merge
            if result == 'skip':
                continue						# skip empty elements
            tot_result += result
            #yield k							# yield for statistics function (in pipeline) but then i cannot return tot_result? TODO
        if len(tot_result) > 0:
            statistics(nbatch, tot_result)				# stastistics are done within each batch but i'd like to skip empty batches!
            tot_tot_result += tot_result				# add the batch to the final result										
            end_batch(context, nbatch)					# check if is ok to skip empty batches like that
    return tot_tot_result

# context.sess.add(result) is done out in the real process_one function (e.g. do_one)

# call the end_batch function:
def end_batch(context, nb):
    print ("end batch number", nb+1)
    pass
    #context.sess.flush()

# statistics performed for each batch - yield got_batch and use .next() for elements and call statistics(got_batch) TODO 
def statistics(nb, res):					
   ok = 0
   not_ok = 0
   tot = 0
   for k in res:
       if k:
           tot = tot+1
       if len(k) > 0:						# add option if result == 'skip' then continue
           ok = ok+1
       else:
           not_ok = not_ok+1 
   print ('FOR BATCH {} IMPORTED {} of {} elements ({:.1%} success rate)'.format(nb+1, ok, tot, ok/(float(tot) + 0.00001)))
   #context.prob() # "problems for this batch are", not_ok


