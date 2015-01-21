from __future__ import absolute_import

from .preprocessing import (CorpusMSAbstracts, CorpusMSAbstracts_Collocations, CorpusMSAbstracts_NER,
                                            CorpusMSAbstractsSimple)

import itertools
import gensim


class CorpusDict(object):
    def __init__(self, corpus, dictionary):
        self.corpus = corpus
        self.dictionary = dictionary

    def __iter__(self):
        for tokens in iter_corpus(self.corpus):
            yield self.dictionary.doc2bow(tokens)


def iter_corpus(corpus):
    for document in corpus:
        yield document


def corpus_bow(corpus, data, filename):
    corpus_tokens = (tokens for tokens in iter_corpus(corpus))
    # Create dictionary out of input corpus tokens
    corpus_dict = gensim.corpora.Dictionary(corpus_tokens)
    # Save dictionary to file
    corpus_dict.save('material_science/output/%s.dict' % filename)
    # Transform corpus to bag_of_words
    corpus_bow = CorpusDict(corpus, corpus_dict)
    # Serialize and save corpus bag of words
    corpus = gensim.corpora.MmCorpus.serialize('material_science/output/%s.mm' % filename, corpus_bow)
    return corpus


def head(stream, n=10):
    """Convenience fnc: return the first `n` elements of the stream, as plain list."""
    return list(itertools.islice(stream, n))


MSR_DATA = 'material_science/data/msr-data'

corpus_simple = CorpusMSAbstractsSimple(MSR_DATA)
corpus_simple_bow = corpus_bow(corpus_simple, MSR_DATA, 'simple')

corpus_collocations = CorpusMSAbstracts_Collocations(MSR_DATA)
corpus_collocations_bow = corpus_bow(corpus_collocations, MSR_DATA, 'collocations')

corpus_ner_only = CorpusMSAbstracts_NER(MSR_DATA)
corpus_ner_bow = corpus_bow(corpus_ner_only, MSR_DATA, 'ner')

corpus_with_ner = CorpusMSAbstracts(MSR_DATA)
corpus_bow = corpus_bow(corpus_with_ner, MSR_DATA, 'corpus')
