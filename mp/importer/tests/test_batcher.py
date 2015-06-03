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


class TestParser(TestCase):

    def create_test_parser(self):								# simulates the parser within the main script
        import argparse
        parser = argparse.ArgumentParser(description='simulates passing arguments to script')
        parser.add_argument('--db', dest='to_db', help="destination database")			# the main script adds all general arguments (9 more)	
        parser.add_argument('--from-db', dest='from_db', help="source database")		
        return parser
	

    def test_Add_arguments(self):
        from .. import batcher
        parser = self.create_test_parser()
        batcher.add_arguments(parser)					
        args = ['./bin/import_from_godengo_batcher.py', '--db', 'test_batcher', '--from-db', 'postgresql:///cityscene', '--batch-size', '10', '--max-batches', '2']
        options = parser.parse_args(args[1:])							# parsing done in the main function and for all arguments except program name
        self.assertEqual(options.batch_size, 10)

    def test_Get_batcher_args_alline(self):
        from .. import batcher
        args = ['./bin/import_from_godengo_batcher.py', '--db', 'test_batcher', '--from-db', 'postgresql:///cityscene', '--batch-size', '10', '--max-batches', '2']
        parser = self.create_test_parser()		
        batcher.add_arguments(parser)
        options = parser.parse_args(args[1:])													 
        result = batcher.get_batcher_args(options)						
        self.assertEqual(result, {'max_batches':2, 'batch_start': 0, 'batch_size':10})


    def test_Get_batcher_args_none(self):
        from .. import batcher
        args = []
        parser = self.create_test_parser()									
        batcher.add_arguments(parser)
        options = parser.parse_args(args[1:])													 
        result = batcher.get_batcher_args(options)						# if input is not specified, default values				
        self.assertEqual(result, {'max_batches': None, 'batch_start': 0, 'batch_size':1000}) 				


    def test_Get_batcher_args_missing_arg(self):
        from .. import batcher
        args = ['./bin/import_from_godengo_batcher.py', '--db', 'test_batcher', '--from-db', 'postgresql:///cityscene', '--batch-size', '10']
        parser = self.create_test_parser()									
        batcher.add_arguments(parser)
        options = parser.parse_args(args[1:])													 
        result = batcher.get_batcher_args(options)						
        self.assertEqual(result, { 'max_batches': None, 'batch_start': 0, 'batch_size': 10}) 	


class FunctionalTest(TestCase):									# To test the whole workflow, similarly to real case

    def create_test_parser(self):								
        import argparse
        parser = argparse.ArgumentParser(description='simulates passing arguments to script')
        parser.add_argument('--db', dest='to_db', help="destination database")			
        parser.add_argument('--from-db', dest='from_db', help="source database")			
        return parser

    def test_all(self):
        from .. import batcher
        args = ['./bin/import_script.py', '--db', 'test_batcher', '--from-db', 'postgresql:///database', '--batch-start', '1', '--batch-size', '3']
        parser = self.create_test_parser()							
        batcher.add_arguments(parser)
        options = parser.parse_args(args[1:])													 
        kw = batcher.get_batcher_args(options)		
        log = []
        def end_batch():                
            log.append('X')
        batcher = batcher.run_in_batches('abcdefg', end_batch, **kw)
        for letter in batcher:
            log.append(letter)
        result = ''.join(log)
        self.assertEqual(result, 'defXgX')								
	

class TestRandom(TestCase):

    def create_test_seed(self):
        import sys
        import random
        seed = random.SystemRandom()								# create random value using system 
        return seed

    def test_random_sampler_percentage(self):
        from .. import batcher
        import logging							
        source = 'abcdefghil'						
        percentage = 50
        kw = dict()
        kw['seed'] = self.create_test_seed()				 
        logging.info('SEED FOR THIS IMPORT: {}'.format(kw['seed']))    				# main script logs seed value
        kw['percentage'] = 50
        result = batcher.random_sampler_2(source, **kw) 					# generator that yields the values
        log=[]
        for element in result:              
            log.append(element)
        log_list = ''.join(log)
        self.assertEqual(len(log_list), 5)							# check that it's yielding the right number of elements

    def test_random_sampler_elements(self):
        from .. import batcher
        source = 'abcdefghil'						
        kw = dict()
        kw['seed'] = 1
        kw['percentage'] = 50
        result = batcher.random_sampler_2(source, **kw)			 	
        log=[]
        for element in result:              
            log.append(element)
        log_list = ''.join(log)
        self.assertEqual(log_list, 'bihce')							# check the elements (knowing the seed, gives always the same result)

    def test_random_sampler_elements_default(self):
        from .. import batcher
        source = 'abcdefghil'						
        kw = dict()
        kw['seed'] = 1
        result = batcher.random_sampler_2(source, **kw)							
        log=[]
        for element in result:              
            log.append(element)
        log_list = ''.join(log)
        self.assertEqual(log_list, 'b')								# 10%, has used the default value

	
# for the test, I pass seed value (so I know the result) but in the reality, seed is generated within the script
# TODO should I use argument parser here and pass more arguments if random!? 
# create functional random test to use also the random and pass arguments

