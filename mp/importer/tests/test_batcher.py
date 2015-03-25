import os
from unittest import TestCase
import collections
from collections import namedtuple
from collections import Iterable
from itertools import *

def make_test_context(b_size, b_start, b_max):									# creates a "provisional" context 
    context = namedtuple('Context', """
        start_batch
        max_batches
        batch_size """)
    context.batch_size = b_size
    context.start_batch = b_start
    context.max_batches = b_max
    return context

# test function (it will be the import function) - generalize for different types of iterable - now writes results in a list with nested lists (to be changed if needed)
def process_one(item):				
    result = []
    if len(item) != 0:
        if isinstance(item, str):
            result.append(item.upper())
        else:
            for x in item:
                result.append(x.upper()) 
        return result
    else:
        return result

class TestBatcher(TestCase):
    # 1- test that the function makes batches of a given size
    def test_Make_Batches(self):
        input_list = ['a','b','c','d'] 									
        context = make_test_context(2,0,3)
        from .. import batcher									
        result = batcher.run_in_batches(context, input_list, process_one)				
        self.assertEqual(result,[['A'],['B'],['C'],['D']])
    #
    # 2- test that the function starts being executed from a specified batch number (batches of given size) and that the max_batches works
    def test_Start_from_Batch(self):
       input_list = ['a','b','c','d','e','f','g','h']									
       context = make_test_context(2,2,1)
       from .. import batcher									
       result = batcher.run_in_batches(context, input_list, process_one)				
       self.assertEqual(result,[['E'],['F']])
 







