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
    def test_batches(self):
        print ("*** test make batches")
        log = []
        def end_batch():				
            log.append('X')
        from .. import batcher
        context = make_test_context(2,0,2)
        batcher = batcher.run_in_batches(		# reads from iterable., creates batches and executes end_batch at the end of each one
                context,
                iter('abcdefghilm'), end_batch)			# ghilm
        for letter in batcher:				# takes the letter yielded by run_in_batches
            log.append(letter)
        self.assertEqual(
                ''.join(log),
                'abXcdX')

# test how to start batch from a given batch number - TODO
    def test_Start_batches(self):
        print ("*** test Start batches")
        log = []
        def end_batch():				
            log.append('X')
        from .. import batcher
        context = make_test_context(2,1,2)
        batcher = batcher.run_in_batches(		# reads from iterable., creates batches and executes end_batch at the end of each one
                context,
                iter('abcdefghilm'), end_batch)			
        for letter in batcher:				# takes the letter yielded by run_in_batches
            log.append(letter)
        self.assertEqual(
                ''.join(log),
                'cdXefX')


# test a batch that is incomplete . call end_batch when there are no elements left - TODO
    def test_Rest_batches(self):
        print ("*** test Rest batches")
        log = []
        def end_batch():				
            log.append('X')
        from .. import batcher
        context = make_test_context(2,0,2)
        batcher = batcher.run_in_batches(		# reads from iterable., creates batches and executes end_batch at the end of each one
                context,
                iter('abcde'), end_batch)			# ghilm
        for letter in batcher:				# takes the letter yielded by run_in_batches
            log.append(letter)
        self.assertEqual(
                ''.join(log),
                'abXcdXeX')











