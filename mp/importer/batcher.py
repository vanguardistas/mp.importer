def get_batches(context, iterable, bmax, bstart):
    count = 0
    for i in iterable:
        count +=1
        current_batch, position_in_batch = divmod(count, context.batch_size)
        if position_in_batch == 0:
            current_batch = current_batch-1						# the last element of a batch has position 0 and value (current_batch+1)
        if current_batch >= bstart and current_batch <= bmax:
            yield i
 
def run_in_batches(context, iterable, end_batch):
    c = 0
    bstart = context.start_batch
    bmax = context.max_batches
    for k in get_batches(context, iterable, bmax, bstart):												
        c = c+1			
        current_batch, position_in_batch = divmod(c, context.batch_size)
        yield k
        if position_in_batch == 0:
            end_batch()
            if current_batch == bmax:
                break   


