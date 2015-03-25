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
        self.assertEqual(result,['A','B','C','D'])
    #
    # 2- test that the function starts being executed from a specified batch number (batches of given size) and that the max_batches works
    def test_Start_from_Batch(self):
       input_list = ['a','b','c','d','e','f','g','h']									
       context = make_test_context(2,2,1)
       from .. import batcher									
       result = batcher.run_in_batches(context, input_list, process_one)				
       self.assertEqual(result,['E','F'])
 
    # 3- check different iterable inputs (including empty) and non-iterable (e.g. set) to make it fail 
    def test_Batcher_input(self):
        test_list = list()
        test_list.append('a') 									# for now i use letters because i still do "upper"
        test_list.append('a')
        test_list.append('x')		# test_list = ('a','a','x'), test_set is same
        test_set = set(test_list)
        test_frozenset = frozenset()
        filename = '/home/kiara/GIT/mp.importer/mp/importer/tests/test.csv'
        openedfile = open(filename, 'r')
        test_row_list = list()
        for row in openedfile:
            test_row = row[:-1]									# in case of file, i read the lines of the file and create a list, that will be then splitted
            test_row_list.append(test_row)
        input_to_test = [test_list, test_set, test_frozenset, set(), list(), test_row_list]   # try list(), set(), tuples
        from .. import batcher	
        context = make_test_context(2,0,3)
        result_list = list()								
        for i in input_to_test:
            if hasattr(i, '__getitem__') is True: 						# __getitem__ is used by the batcher function! replaced by next!
                result = batcher.run_in_batches(context, i, process_one)			
                result_list.append(result) 
            else:	
                #print i									
                pass
                #self.fail()									# non-iterable should fall in here -  test_set, test_frozenset, set()
        self.assertEqual(result_list,[['A','A', 'X'], [], ['CHIARA', 'ANNA', 'XXX', 'X']])	 # empty list gives this... [[], []] change in code to skip empty things!






