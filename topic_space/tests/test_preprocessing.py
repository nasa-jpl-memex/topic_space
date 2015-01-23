"""
Automated tests for pre-processing package
"""

import logging
import unittest
import os
import os.path
import tempfile

from topic_space.preprocessing import (CorpusCollocationsTokenizer, CorpusMixedTokenizer,
                                       CorpusNERTokenizer, CorpusSimpleTokenizer)

module_path = os.path.dirname(__file__)
datapath = os.path.join(module_path, "test_data")

class TestSimpleTokenizer(unittest.TestCase):
    def setUp(self):
        self.data = datapath

    def testTokenizer(self):
        "test simple tokenizer"
        corpus = CorpusSimpleTokenizer(self.data)

        expected = []

        self.assertTrue()

