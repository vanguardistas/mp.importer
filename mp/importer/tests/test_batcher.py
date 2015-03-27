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

    def test_Max_batches(self):
        print ("*** test Max batches")
        log = []
        def end_batch():				
            log.append('X')
        from .. import batcher
        context = make_test_context(2,0,10)
        batcher = batcher.run_in_batches(		# reads from iterable., creates batches and executes end_batch at the end of each one
                context,
                iter('abcdefghil'), end_batch)			# ghilm
        for letter in batcher:				# takes the letter yielded by run_in_batches
            log.append(letter)
        self.assertEqual(
                ''.join(log),
                'abXcdXefXghXilX')

    def test_Size_batches(self):
        print ("*** test Size batches")
        log = []
        def end_batch():				
            log.append('X')
        from .. import batcher
        context = make_test_context(3,0,2)
        batcher = batcher.run_in_batches(		# reads from iterable., creates batches and executes end_batch at the end of each one
                context,
                iter('abcdefghilm'), end_batch)			# ghilm
        for letter in batcher:				# takes the letter yielded by run_in_batches
            log.append(letter)
        self.assertEqual(
                ''.join(log),
                'abcXdefX')

# test how to start batch from a given batch number
    def test_Start_batches(self):
        print ("*** test Start batches")
        log = []
        def end_batch():				
            log.append('X')
        from .. import batcher
        context = make_test_context(2,1,3)
        batcher = batcher.run_in_batches(		# reads from iterable., creates batches and executes end_batch at the end of each one
                context,
                iter('abcdefghilm'), end_batch)			
        for letter in batcher:				# takes the letter yielded by run_in_batches
            log.append(letter)
        if log[-1] != 'X':
            end_batch() 
        self.assertEqual(
                ''.join(log),
                'cdXefXghX')


# test a batch that is incomplete . call end_batch when there are no elements left - TODO
    def test_Rest_batches(self):
        print ("*** test Rest batches")
        log = []
        def end_batch():				
            log.append('X')
        from .. import batcher
        context = make_test_context(2,0,3)
        batcher = batcher.run_in_batches(		# reads from iterable., creates batches and executes end_batch at the end of each one
                context,
                iter('abcde'), end_batch)			# ghilm
        for letter in batcher:				# takes the letter yielded by run_in_batches
            log.append(letter)
        self.assertEqual(
                ''.join(log),
                'abXcdXeX')










