from __future__ import absolute_import

from topic_space.preprocessing import CorpusSimpleTokenizer

import gensim

def iter_corpus(corpus):
    for document in corpus:
        yield document


class CorpusDict(object):
    """
    A Dictionary constructed from a corpus (collection of documents).

    Parameters
    ----------
    corpus: A collection of documents
        Each document is a list of tokens = tokenized and normalized strings (either utf8 or unicode).
        (e.g. CorpusMSAbstractsSimple, CorpusMSAbstracts_Collocations, CorpusMSAbstracts_NER or CorpusMSAbstractsSimple)
    filename: string
        The desired filename for the generated dictionary
    >>> my_corpus = CorpusSimpleTokenizer("my_data")
    >>> corpus_dictionary = CorpusDict(my_corpus, "My lda results")
    """

    def __init__(self, corpus, filename):
        self.corpus = corpus
        self.filename = filename

    def create(self):
        corpus_tokens = (tokens for tokens in iter_corpus(self.corpus))
        # Create dictionary out of input corpus tokens
        corpus_dict = gensim.corpora.Dictionary(corpus_tokens)
        # Save dictionary to file
        corpus_dict.save(self.filename)

        return corpus_dict


class CorpusBOW(object):
    """
    A bag-of-words representation of a corpus (collection of documents).

    Parameters
    ----------
    corpus: A collection of documents
        Each document is a list of tokens = tokenized and normalized strings (either utf8 or unicode).
        (e.g. CorpusMSAbstractsSimple, CorpusMSAbstracts_Collocations, CorpusMSAbstracts_NER or CorpusMSAbstractsSimple)
    dictionary: gensim.corpora.dictionary.Dictionary class
        Dictionary to be use in the bag-of-words vector space
    >>> my_corpus = CorpusSimpleTokenizer("my_data")
    >>> my_dict = CorpusDict(my_corpus, "my_dict.dict")
    >>> corpus_bow = CorpusBOW(my_corpus, my_dict)
    """

    def __init__(self, corpus, dictionary):
        self.corpus = corpus
        self.dictionary = dictionary

    def __iter__(self):
        for tokens in iter_corpus(self.corpus):
            yield self.dictionary.doc2bow(tokens)

    def serialize(self, filename):
        """
        Serialize a corpus (collection of documents) in a bag-of-words vector space to a Matrix Market Exchange Format.
        http://math.nist.gov/MatrixMarket/formats.html

        Parameters
        ----------
        filename: string
            The filename for the stored serialized corpus
        >>> my_corpus = CorpusSimpleTokenizer("my_data")
        >>> my_dict = CorpusDict(my_corpus, "my_dict.dict")
        >>> CorpusBOW(my_corpus, my_dict).serialize("my_serialized_corpus")
        """
        # Serialize and save corpus bag of words
        corpus = gensim.corpora.MmCorpus.serialize(filename, self)
        return corpus