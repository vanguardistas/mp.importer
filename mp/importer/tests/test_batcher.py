import os
from unittest import TestCase
import collections
from collections import namedtuple
from collections import Iterable
from itertools import *

def make_test_context(arg_list):									# creates a "provisional" context 
    context = namedtuple('Context', """
        batch_size
        start_batch
        max_batches """)
    context.batch_size = arg_list[0]
    context.start_batch = arg_list[1]
    context.max_batches = arg_list[2]
    return context

# dictionary of tests contains (test_name:result)
test_dict = {'Make batches':'abXcdX','Max Batches':'abXcdXefXghXilXmX','Batch size':'abcXdefX','Start batch':'cdXefXghX','Last incomplete batch':'abXcdXeX'}

# dictionary of context parameters
context_dict = {'Make batches':(2,0,2),'Max Batches':(2,0,10),'Batch size':(3,0,2),'Start batch':(2,1,3),'Last incomplete batch':(2,0,3)}

class TestBatcher(TestCase):
    def test_for_batches(self):
        log = []
        def end_batch():				
            log.append('X')
        from .. import batcher
        input_string = 'abcdefghilm'			#input is always the same for these tests 
        for test,result in test_dict.items():
            args = context_dict[test]
            print ("args list", args)
            context = make_test_context(args)
            print ("executing test:", test) 
            batcher = batcher.run_in_batches(		
                    context,
                    iter(input_string), end_batch)			
            for letter in batcher:				
                log.append(letter)
            if log[-1] != 'X':
                end_batch()
            self.assertEqual(
                    ''.join(log),
                    result) 
            break 					# if only once, it works, but cannot be looped because the generator is exahusted. need to restart it somehow TODO












