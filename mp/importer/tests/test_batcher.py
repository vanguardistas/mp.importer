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
	

    def test_Parse_arguments(self):
        from .. import batcher
        parser = self.create_test_parser()
        parser = batcher.parse_arguments(parser)						
        args = ['./bin/import_from_godengo_batcher.py', '--db', 'test_batcher', '--from-db', 'postgresql:///cityscene', '--batch-size', '10', '--max-batches', '2']
        options = parser.parse_args(args[1:])							# parsing done in the main function and for all arguments except program name
        result = []  										
        result.append(options.batch_size)
        result.append(options.max_batches)
        self.assertEqual(result, [10, 2])


    def test_Get_batcher_args_alline(self):
        from .. import batcher
        args = ['./bin/import_from_godengo_batcher.py', '--db', 'test_batcher', '--from-db', 'postgresql:///cityscene', '--batch-size', '10', '--max-batches', '2']
        parser = self.create_test_parser()									
        parser = batcher.parse_arguments(parser)
        options = parser.parse_args(args[1:])													 
        result = batcher.get_batcher_args(options)						
        self.assertEqual(result, {'batch_size':10 , 'max_batches':2})


    def test_Get_batcher_args_none(self):
        from .. import batcher
        args = []
        parser = self.create_test_parser()									
        parser = batcher.parse_arguments(parser)
        options = parser.parse_args(args[1:])													 
        result = batcher.get_batcher_args(options)						# if input is not specified, batcher gives default values				
        self.assertEqual(result, {}) 				


    def test_Get_batcher_args_missing_arg(self):
        from .. import batcher
        args = ['./bin/import_from_godengo_batcher.py', '--db', 'test_batcher', '--from-db', 'postgresql:///cityscene', '--batch-size', '10']
        parser = self.create_test_parser()									
        parser = batcher.parse_arguments(parser)
        options = parser.parse_args(args[1:])													 
        result = batcher.get_batcher_args(options)						
        self.assertEqual(result, {'batch_size': 10}) 	

    def test_Get_batcher_args_less_args(self):
        from .. import batcher
        args = ['./bin/import_from_godengo_batcher.py', '--db', 'test_batcher', '--batch-size', '10']
        parser = self.create_test_parser()									
        parser = batcher.parse_arguments(parser)
        options = parser.parse_args(args[1:])													 
        result = batcher.get_batcher_args(options)						
        self.assertEqual(result, {'batch_size': 10}) 


class TestAll(TestCase):									# To test the whole workflow, similarly to real case

    def create_test_parser(self):								
        import argparse
        parser = argparse.ArgumentParser(description='simulates passing arguments to script')
        parser.add_argument('--db', dest='to_db', help="destination database")			
        parser.add_argument('--from-db', dest='from_db', help="source database")			
        return parser

    def test_all(self):
        from .. import batcher
        args = ['./bin/import_from_godengo_batcher.py', '--db', 'test_batcher', '--from-db', 'postgresql:///cityscene', '--batch-start', '1', '--max-batches', '1']
        parser = self.create_test_parser()							
        parser = batcher.parse_arguments(parser)
        options = parser.parse_args(args[1:])													 
        kw = batcher.get_batcher_args(options)		
        log = []
        def end_batch():                
            log.append('X')
        batcher = batcher.run_in_batches('abcdefg', end_batch, **kw)
        for letter in batcher:
            log.append(letter)
        result = ''.join(log)
        self.assertEqual(result, 'cdX')								
	



