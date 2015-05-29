import os
from unittest import TestCase
import collections
from collections import namedtuple
from collections import Iterable
from itertools import *


class TestBatcher(TestCase):

    def one(self, source, **kw): 								# **kw allows passing only some keyworks (the others will be set to default by batcher), easier for user
        log = []
        def end_batch():                
            log.append('X')
        from .. import batcher
        batcher = batcher.run_in_batches(source, end_batch, **kw)				# pass direclty **kw to batcher
        for letter in batcher:              
            log.append(letter)
        return ''.join(log)

    def test_Make_batches(self):
        result = self.one('abcdefg')			
        self.assertEqual(result, 'abXcdXefXgX')		

    def test_Make_big_batches(self):								# one incomplete batch of maximum 1000 elements
        result = self.one('abcdefg', batch_size=1000)			
        self.assertEqual(result, 'abcdefgX')

    def test_Max_batches(self):
        result = self.one('abcdefg', max_batches=2)
        self.assertEqual(result, 'abXcdX')

    def test_Batch_size(self):
        result = self.one('abcdefg', batch_size=3, max_batches=2)
        self.assertEqual(result, 'abcXdefX')

    def test_Start_batch(self):
        result = self.one('abcdefg', batch_start=2, max_batches=3)  				# batch_start=1 means skipping the first batch (the 0-batch)
        self.assertEqual(result, 'efXgX')		

    def test_End_iterator(self):
        result = self.one('abc', batch_size=2, max_batches=2)
        self.assertEqual(result, 'abXcX')


    def test_Parse_arguments(self):
        from .. import batcher
        args =  ["--argument_1", "10", "--argument_2", "2"] 					# sys.argv returns a list like this, this function can take CL inputs					
        options = batcher.parse_arguments(args)
        result = []  										# option is Namespace(argument_1=10),
        result.append(options.batcher_argument_1)
        result.append(options.batcher_argument_2)
        self.assertEqual(result, [10, 2])


    def test_Get_batcher_args(self):
        from .. import batcher
        args = ["--argument_1", "10", "--argument_2", "2"]									
        options = batcher.parse_arguments(args)
        result = batcher.get_batcher_args(options)						# options is a namespace returned by argparse, batcher_args is a dictionary **kw
        self.assertEqual(result, {'batcher_argument_1':10 , 'batcher_argument_2':2})
 
    # TODO make it work directly with output of sys.argv, need to know the script arguments and order - generalize!?
    def test_Get_batcher_args_allstring(self):
        from .. import batcher
        args = ['./bin/import_from_godengo_batcher.py', '--db', 'test_batcher', '--from-db', 'postgresql:///cityscene', '--argument_1', '10', '--argument_2', '2']				
        newargs = args[5:]
        print (newargs)
        options = batcher.parse_arguments(newargs)
        result = batcher.get_batcher_args(options)						# options is a namespace returned by argparse, batcher_args is a dictionary **kw
        self.assertEqual(result, {'batcher_argument_1':10 , 'batcher_argument_2':2}) 







