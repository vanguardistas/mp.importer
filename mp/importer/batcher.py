# this function is intentionally get empty for now
# this program takes an iterable and splits in a number of batches using the batch_size argument (from context)
# result is a list that contains the batches (for now)

def run_in_batches(context, iterable, process_one): 		
    num = int(len(iterable))                                      
    batch_size = context.batch_size
    start_batch = context.start_batch					
    batch_stop, extra = divmod(num, batch_size)
    if start_batch == 0:
        list = []
        if extra == 0:								
            for n in range(0,batch_stop):												
                batch_item = iterable[n*batch_size:batch_size+n*batch_size] 	
                result = process_one(batch_item)
                list.append(result)
        else:
            for n in range(0,batch_stop):					
                batch_item = iterable[n*batch_size:batch_size+n*batch_size]	
                result = process_one(batch_item)
                list.append(result)
            last_item = iterable[batch_stop*batch_size:]
            result = process_one(last_item)
            list.append(result)
        return list  
    else:								# here starts from some batch specified by context (loops can be merged because it's a specific case when start_batch = 0)
        list = []
        if extra == 0:								
            for n in range(start_batch,batch_stop):					
                batch_item = iterable[n*batch_size:batch_size+n*batch_size]	
                result = process_one(batch_item)
                list.append(result)
        else:
            for n in range(start_batch,batch_stop):					
                batch_item = iterable[n*batch_size:batch_size+n*batch_size]	
                result = process_one(batch_item)
                list.append(result)
            last_item = iterable[batch_stop*batch_size:]
            result = process_one(last_item)
            list.append(result)
        return list

# TODO
# https://docs.python.org/2/library/itertools.html see itertools documentation for random batcher
#def random_combination(iterable, r):
 #   "Random selection from itertools.combinations(iterable, r)"
 #   pool = tuple(iterable)
 #   n = len(pool)
 #   indices = sorted(random.sample(xrange(n), r))
 #   return tuple(pool[i] for i in indices)

