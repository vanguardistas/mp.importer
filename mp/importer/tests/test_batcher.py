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
    if len(item) == 0 or item is None:
        return 'skip'
    else:
        if isinstance(item, str):
            result.append(item.upper())
        else:
            for x in item:
                result.append(x.upper()) 
        return result

class TestBatcher(TestCase):
    # 1- test that the function makes batches of a given size
    def test_Make_Batches(self):
        print ("test Make Batches")
        input_list = ['a','b','c','d'] 									
        context = make_test_context(2,0,2)			# there is no problem if end_batch is 100 because the loop ends when the iterator ends
        from .. import batcher									
        result = batcher.run_in_batches(context, input_list, process_one)				
        self.assertEqual(result,['A','B','C','D'])
    #
    # 2- test that the function starts being executed from a specified batch number (batches of given size) and that the max_batches works
    def test_Start_from_Batch(self):
        print ("test Start from batch")
        input_list = ['a','b','c','d','e','f','g','h']									
        context = make_test_context(2,2,1)
        from .. import batcher									
        result = batcher.run_in_batches(context, input_list, process_one)				
        self.assertEqual(result,['E','F'])

    # 3- test that the function skips empty batches
    def test_Skip_empty_batch(self):
        print ("test Skip empty batch")
        input_list = ['a','b','','','e','f','g','h']									
        context = make_test_context(2,0,2)
        from .. import batcher									
        result = batcher.run_in_batches(context, input_list, process_one)				
        self.assertEqual(result,['A','B'])

    # 4- test with arbitrary big max_batches number (will be set to 100 by default)
    def test_Max_batches(self):
        print ("test max batches")
        input_list = ['a','b','','','e','f','g','h','i']									
        context = make_test_context(2,0,100)
        from .. import batcher									
        result = batcher.run_in_batches(context, input_list, process_one)				
        self.assertEqual(result,['A','B','E','F','G','H','I'])

    # 5- test with arbitrary big max_batches number (will be set to 100 by default)
    def test_Batch_size(self):
        print ("test batch size")
        input_list = ['a','b','c','d','e','f','g']									
        context = make_test_context(3,0,3)
        from .. import batcher									
        result = batcher.run_in_batches(context, input_list, process_one)				
        self.assertEqual(result,['A','B','C','D','E','F','G'])

     # 6- test with csv file
    def test_Batcher_input(self):
        print ("test batcher input csv file")
        filename = '/home/kiara/GIT/mp.importer/mp/importer/tests/test.csv'
        openedfile = open(filename, 'r')
        test_row_list = list()
        for row in openedfile:
            test_row = row[:-1]									# read the lines of the file and create a list, that will be then splitted 
            test_row_list.append(test_row)
        input_to_test = [test_row_list]   # try list(), set(), tuples
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
                #self.fail()									# non-iterable fall in here -  test_set, test_frozenset, set()
        self.assertEqual(result_list,[['CHIARA,ANNA', 'ANNA,CHIARA', 'XXX,', 'X']])	 # nb: takes the entire line of the csv



