import os
from unittest import TestCase
import collections
from collections import namedtuple
from collections import Iterable
from itertools import *

def make_test_options(batch_size=2, batch_start=0, max_batches=10):							# creates a "provisional" options, set default in case **kw none 
    options = namedtuple('Options', "batch_size, start_batch, max_batches")
    options.batch_size = batch_size
    options.batch_start = batch_start
    options.max_batches = max_batches
    return options

class TestBatcher(TestCase):

    def one(self, source, **kw): 								# **kw allows passing only some keyworks (the others will be set to default by batcher) -easier for user
        log = []
        def end_batch():                
            log.append('X')
        from .. import batcher
        options = make_test_options(**kw)							#batch_size, batch_start, max_batches)
        batcher = batcher.run_in_batches_with_options(source, end_batch, options) 		
        for letter in batcher:              
            log.append(letter)
        return ''.join(log)

    def test_Make_batches(self):
        result = self.one('abcdefg')			
        self.assertEqual(result, 'abXcdXefXgX')		

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




