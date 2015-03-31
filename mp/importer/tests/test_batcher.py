import os
from unittest import TestCase
import collections
from collections import namedtuple
from collections import Iterable
from itertools import *

def make_test_context(b_size, b_start, b_max):									# creates a "provisional" context 
    context = namedtuple('Context', """
        batch_size
        start_batch
        max_batches """)
    context.batch_size = b_size
    context.start_batch = b_start
    context.max_batches = b_max
    return context

class TestBatcher(TestCase):

    def one(self, source, batch_size=2, batch_start=0, max_batches=10):					# batch size cannot be 0
        log = []
        def end_batch():                
            log.append('X')
        from .. import batcher
        context = make_test_context(batch_size, batch_start, max_batches)
        batcher = batcher.run_in_batches(       
                context,
                source, end_batch)          
        for letter in batcher:              
            log.append(letter)
        if log[-1] != 'X':
            end_batch()
        return ''.join(log)

    def test_batches(self):
        result = self.one('abcdefg')			# check it with None when changed the code (default is None)
        self.assertEqual(result, 'abXcdXefXgX')

    def test_Max_batches(self):
        result = self.one('abcdefg', max_batches=2)
        self.assertEqual(result, 'abXcdX')

    def test_Batch_size(self):
        result = self.one('abcdefg', batch_size=3, max_batches=2)
        self.assertEqual(result, 'abcXdefX')

    def test_Start_batch(self):
        result = self.one('abcdefg', batch_start=1, max_batches=2)  # batch_start=1 means skipping the first batch (the 0-batch)
        self.assertEqual(result, 'cdXefX')

    def test_With_csv(self):
        filename = '/home/kiara/GIT/mp.importer/mp/importer/tests/test.csv'
        openedfile = open(filename, 'r')
        iterable = list()
        for row in openedfile:
            test_row = row[:-1]									 
            iterable.append(test_row)
            result = self.one(iterable, batch_start=0, max_batches=1)
        self.assertEqual(result, 'chiara-anna-X')			# batch_size = 2, takes the first two elements of the list (first and second row of csv)




