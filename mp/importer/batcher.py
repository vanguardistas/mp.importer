
def run_in_batches(iterable, end_batch_callback, batch_size, start_batch, max_batches):					# arguments passed through "options"
    c = 0
    ended = False
    for k in iterable:
        c = c+1			
        current_batch, position_in_batch = divmod(c, batch_size)
        if position_in_batch == 0:
            current_batch = current_batch-1						# last element of a batch has position=0, value=current_batch+1
        if current_batch >= start_batch and current_batch < start_batch+max_batches:
            ended = False
            yield k 
            if position_in_batch == 0: 							# ends completed batches
                end_batch_callback()
                ended = True
        if current_batch == start_batch+max_batches:						# if gets maximum allowed batches, break 
            break
    if ended is False:
        end_batch_callback()	


def run_in_batches_with_options(iterable, end_batch_callback, options):
    for x in run_in_batches (iterable, end_batch_callback, options.batch_size, options.start_batch, options.max_batches):
        yield x

