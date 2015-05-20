def run_in_batches(context, iterable, end_batch):
    c = 0
    bstart = context.start_batch
    bmax = context.max_batches
    for k in iterable:												
        c = c+1			
        current_batch, position_in_batch = divmod(c, context.batch_size)
        if position_in_batch == 0:
            current_batch = current_batch-1						# last element of a batch: position=0, value=current_batch+1
        if current_batch >= bstart and current_batch < bstart+bmax:
            yield k 
            if position_in_batch == 0: 							# ends all completed batches
                end_batch()
        if current_batch == bstart+bmax:						# if gets maximum allowed batches, break 
            break 
    end_batch()							# if iterator has finished, or if break because of max_batches, end_batch()
                


