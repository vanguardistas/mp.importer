import os
from unittest import TestCase
import collections
from collections import namedtuple
from collections import Iterable

def make_test_context_1():									# creates a "provisional" context 
    context = namedtuple('Context', """
        start_batch
        batch_size """)
    context.batch_size = 2									# batcher will read it from context in the script
    context.start_batch = 0
    return context

def make_test_context_2():									 
    context = namedtuple('Context', """
        start_batch
        batch_size """)
    context.batch_size = 2									
    context.start_batch = 2
    return context

# test function (it will be the import function) - generalize for different types of iterable - now writes results in a list with nested lists (to be changed if needed)
def process_one(item):
    result = []
    if isinstance(item, str):
        result.append(item.upper())
    else:
        for x in item:
            result.append(x.upper()) 
    return result

def process_one_simple(item):
    result = []
    result.append(item.upper())
    return result
# remember that batch_item is a piece of an iterable, done like this batch_item = iterable[n*batch_size:batch_size+n*batch_size] - can be done only for objects that have __getitem__

class TestBatcher(TestCase):
    # 1- test that the function makes batches of a given size
    def test_Make_Batches(self):
        input_string = 'abcdefg'									
        context = make_test_context_1()
        from .. import batcher									
        result = batcher.run_in_batches(context, input_string, process_one_simple)				
        self.assertEqual(result,[['AB'], ['CD'], ['EF'], ['G']])
    #
    # 2- test that the function starts being executed from a specified batch number (batches of given size)
    def test_Start_from_Batch(self):
        input_string = 'abcdefg'									
        context = make_test_context_2()
        from .. import batcher									
        result = batcher.run_in_batches(context, input_string, process_one_simple)				
        self.assertEqual(result,[['EF'], ['G']])
    #
    # 3- test if inputs of the function are iterables or not
    def test_Batcher_iterables(self):
        ok = 0
        not_ok = 0
        test_tuple = ('a','b',1)
        test_list = ['a','b',1]
        test_set = set(test_list)    # set are iterable!
        test_No_obj = None
        test_number = 1233454
        test_string = 'chiara'
        filename = '/home/kiara/GIT/mp.importer/mp/importer/tests/test.csv'
        test_file = open(filename, 'r') 
        input_to_test = [test_set, test_list, test_string, test_tuple, test_file, test_No_obj, test_number] 
        for intest in input_to_test:
            try:
                intest_iterator = iter(intest) 							# valid both for __iter__ and __getitem__ method (str and files respectively)
                ok = ok + 1
            except:
                not_ok = not_ok + 1
        self.assertEqual(ok, 5)
        self.assertEqual(not_ok, 2)

    # 4- check different iterable inputs (including empty) and non-iterable (e.g. set) to make it fail 
    def test_Batcher_input(self):
        test_list = list()
        test_list.append('a') 									# for now i use letters because i still do "upper"
        test_list.append('a')
        test_list.append('x')
        test_set = set(test_list)
        test_frozenset = frozenset()
        filename = '/home/kiara/GIT/mp.importer/mp/importer/tests/test.csv'
        openedfile = open(filename, 'r')
        test_row_list = list()
        for row in openedfile:
            test_row = row[:-1]									# in case of file, i read the lines of the file and create a list, that will be then splitted
            test_row_list.append(test_row)
        input_to_test = ['', 'abcd', '111', test_set, test_frozenset, test_list, set(), list(), test_row_list]   # try list(), set(), tuples
        from .. import batcher	
        context = make_test_context_1()
        result_list = list()								
        for i in input_to_test:
            if hasattr(i, '__getitem__') is True: 						# __getitem__ is used by the batcher function!
                result = batcher.run_in_batches(context, i, process_one)			
                result_list.append(result) 
            else:										
                pass
                #self.fail()									# non-iterable should fall in here - set and frozenset fall here because don't have __getitem__
        self.assertEqual(result_list,[[], [['AB'], ['CD']], [['11'], ['1']], [['A','A'], ['X']], [], [['CHIARA', 'ANNA'], ['XXX', 'X']]])	
    #


# if the csv is opened in bynary mode, py34 adds a 'b' in the string invalidating the assertion - for now reading in text mode
# if not you could also use decode but does not seem to work - row.decode('utf8')
# 
# *** test 3-4:
#isinstance(i, collections.Iterable): does not work for sets, but I'm using getitem!!! 
# set and frozenset are not iterable, but TODO - try different ways because in test-3 they are considered iterable!!!!
#try: intest_iterator = iter(i) also works
# nb: hasattr(i, '__getitem__') is False: not valid for strings! same for __iter__, not valid for file!
# self.assertIsInstance(i, collections.Iterable) could also be a test itself

 







