from __future__ import absolute_import

from topic_space.preprocessing import (CorpusSimpleTokenizer, CorpusNERTokenizer, CorpusMixedTokenizer,
                                       CorpusCollocationsTokenizer)
from topic_space.vector_space import CorpusBOW, CorpusDict
from topic_space.models import LDA
from topic_space.visualizations import Termite

if __name__ == "__main__":

    MSR_DATA = 'material_science/data/msr-data'

    # Tokenize the corpus
    corpus = CorpusSimpleTokenizer(MSR_DATA)

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