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
            if position_in_batch == 0: 
                end_batch()
        if current_batch == bstart+bmax:
            break 

	# TODO end imcomplete batches with 'X' (remove from "one")


