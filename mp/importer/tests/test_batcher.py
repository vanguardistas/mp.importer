import os
from unittest import TestCase
import collections
from collections import namedtuple
from collections import Iterable
from itertools import *


def create_test_options(args=None):							# this function is similar to Parse_arguments: it takes a list of arguments, creates a parser and returns it 
    import argparse
    parser = argparse.ArgumentParser()	
    parser.add_argument('--argument_1', dest='argument_1', type=int, help="1st argument")
    parser.add_argument('--argument_2', dest='argument_2', type=int, help="2nd argument")
    options = None
    if args is not None: 
        options = parser.parse_args(args)
    return options 


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
        args =  ["--argument_1", "10", "--argument_2", "2"] 					#TODO pass the input such as in command line: args = ['--argument_1 10','--argument_2 20']
        options = batcher.parse_arguments(args)
        #print options
        result = []  										# option is Namespace(argument_1=10),
        result.append(options.argument_1)
        result.append(options.argument_2)
        self.assertEqual(result, [10, 2])


    def test_Get_batcher_args(self):
        from .. import batcher
        args = ["--argument_1", "10", "--argument_2", "2"]					#TODO pass the input such as in command line				
        #options = create_test_options(args)							# similar to calling parse_arguments, but the test version, but i can test both functions here
        options = batcher.parse_arguments(args)
        result = batcher.get_batcher_args(options)						# options is a namespace returned by argparse, batcher_args is a dictionary **kw
        self.assertEqual(result, {'argument_1':10 , 'argument_2':2})
 







