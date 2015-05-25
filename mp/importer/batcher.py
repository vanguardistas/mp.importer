def run_in_batches(context, iterable, end_batch):					# TODO remove context and pass parameters
    c = 0
    ended = False
    bstart = context.start_batch
    bmax = context.max_batches
    for k in iterable:
        c = c+1			
        current_batch, position_in_batch = divmod(c, context.batch_size)
        if position_in_batch == 0:
            current_batch = current_batch-1						# last element of a batch has position=0, value=current_batch+1
        if current_batch >= bstart and current_batch < bstart+bmax:
            ended = False
            yield k 
            if position_in_batch == 0: 							# ends completed batches
                end_batch()
                ended = True
        if current_batch == bstart+bmax:						# if gets maximum allowed batches, break 
            break
    if ended is False:
        end_batch()	
