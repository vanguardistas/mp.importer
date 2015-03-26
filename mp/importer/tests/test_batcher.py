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
        log = []
        def end_batch():				# appends x at the end of each batch
            log.append('X')
        from .. import batcher
        context = make_test_context(2,0,2)
        batcher = batcher.run_in_batches(		# reads from iterable and executes end_batch
                context,
                iter('abcdef'), end_batch)
        for letter in batcher:				# takes the letter yielded by run_in_batches
            log.append(letter)
        self.assertEqual(
                ''.join(log),
                'abXcd')




