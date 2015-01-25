from __future__ import absolute_import

import unittest
import os

from topic_space.preprocessing import (CorpusSimpleTokenizer, CorpusNERTokenizer, CorpusMixedTokenizer,
                                       CorpusCollocationsTokenizer)
from topic_space.vector_space import CorpusBOW, CorpusDict
from topic_space.models import LDA
from topic_space.visualizations import Termite

module_path = os.path.dirname(__file__)
data = os.path.join(module_path, "test-data")
token_data = os.path.join(module_path, "test-tokenize")

class SimpleTokenizerTest(unittest.TestCase):

    def setUp(self):
        self.data = data
        self.token_data = token_data

    def test_simple_tokenize_data(self):
        corpus_simple = CorpusSimpleTokenizer(self.data)
        expected = []
        # Assess tokenization behaves as expected
        self.assertTrue()

    def test_create_dictionary(self):
        corpus_dict = CorpusDict(corpus_simple, 'corpus_simple_test.dict').create()
        expected = []
        # Asses

    def tearDown(self):


MSR_DATA = 'test_data'

# Tokenize the corpus
corpus_simple = CorpusSimpleTokenizer(MSR_DATA)
corpus_dict = CorpusDict(corpus_simple, 'corpus_simple.dict').create()
corpus_bow = CorpusBOW(corpus_simple, corpus_dict)
corpus_bow.serialize('corpus_simple.mm')
lda = LDA('corpus_simple.mm', 'corpus_simple.dict')

# You have three other options to tokenize the corpus:
# corpus = CorpusNERTokenizer(MSR_DATA)
# corpus = CorpusMixedTokenizer(MSR_DATA)
# corpus = CorpusCollocationsTokenizer(MSR_DATA)

# Create dictionary
corpus_dict = CorpusDict(corpus, 'corpus.dict').create()

# Transform corpus to bag-of-words vector space
corpus_bow = CorpusBOW(corpus, corpus_dict)
# Serialize and store the corpus
corpus_bow.serialize('corpus.mm')
# Create LDA model from corpus and dictionary
lda = LDA('corpus.mm', 'corpus.dict')

# Generate the input for the termite plot
lda.generate_termite_input('termite.csv')

# Get termite plot for this model
termite = Termite('termite.csv', "My Simple Tokenized LDA Termite Plot")
termite.plot()
