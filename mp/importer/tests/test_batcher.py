import os
from unittest import TestCase
import collections
from collections import namedtuple
from collections import Iterable
from itertools import *


def create_test_options(args=None):							# this function is similar to Parse_arguments: it takes a list of arguments, creates a parser and returns it 
    import argparse
    parser = argparse.ArgumentParser()	
    parser.add_argument('--argument_1', dest='argument_1', type=int, help="First arg")
    options = None
    if args is not None: 
        options = parser.parse_args(args)
        #print ("options.argument_1 is: ", options.argument_1)
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
        args =  ["--argument_1", "10"]	 								#TODO pass the input such as in command line: args = ['--argument_1 10','--argument_2 20']
        options = batcher.parse_arguments(args)
        #print options  										# option is Namespace(argument_1=10),  self.assertIsInstance(options, dict)?
        result = options.argument_1
        self.assertEqual(result, 10)


    def test_Get_batcher_args(self):
        from .. import batcher
        args = ["--argument_1", "10"]									#TODO pass the input such as in command line				
        #options = create_test_options(args)								# similar to calling parse_arguments, but the test version, but i can test both functions here
        options = batcher.parse_arguments(args)
        result = batcher.get_batcher_args(options)							# options is a namespace returned by argparse, batcher_args is a dictionary **kw
        self.assertEqual(result, {'argument_1':10})

 


# NB: options is an object like this:
#Namespace(batch_size=3, commit=False, db='test_batcher', db_host=None, from_db='postgresql:///cityscene', locations=None, loglevel=20, max_batches=1, pages=None, problems='/home/kiara/test_batcher/importer/logs/import_problems.csv', random_batcher=None, start_imp_batch=None, with_blobs=False, with_locations=False)






