import logging
import itertools
import json
import pandas as pd
import gensim
import re

from textblob import TextBlob

import nltk
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures

from gensim.parsing.preprocessing import STOPWORDS


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def iter_material_science_abstracts(filename):
    with open(filename, 'r') as f:
       for line in f.readlines():
            document = json.loads(line)
            print line
            abstract = document.get('abstract')
            print abstract
            yield abstract



class CorpusSimpleTokenizer(object):
    """
    Simple Corpus from material science proceedings abstracts:
     - simply lowercase & match alphabetic chars
     - remove stopwords using gensim.parsing.preprocessing.STOPWORDS.
    """
    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        for text in iter_material_science_abstracts(self.filename):
            # tokenize each message; simply lowercase & match alphabetic chars, for now
            tokenized_text = self.split_words(text)
            yield tokenized_text

    def split_words(self, text, stopwords=STOPWORDS):
        """
        Break text into a list of single words. Ignore any token that falls into
        the `stopwords` set.

        """
        return [word
                for word in gensim.utils.tokenize(text, lower=True)
                if word not in STOPWORDS]

#corpus_simple = CorpusMSAbstractsSimple('material_science/data/msr-data')


def best_ngrams(words, top_n=10000, min_freq=50):
    """
    Extract `top_n` most salient collocations (bigrams and trigrams),
    from a stream of words. Ignore collocations with frequency
    lower than `min_freq`.

    This fnc uses NLTK for the collocation detection itself -- not very scalable!

    Return the detected ngrams as compiled regular expressions, for their faster
    detection later on.

    """
    tcf = TrigramCollocationFinder.from_words(words)
    tcf.apply_freq_filter(min_freq)
    trigrams = [' '.join(w) for w in tcf.nbest(TrigramAssocMeasures.chi_sq, top_n)]
    logging.info("%i trigrams found: %s..." % (len(trigrams), trigrams[:20]))

    bcf = tcf.bigram_finder()
    bcf.apply_freq_filter(min_freq)
    bigrams = [' '.join(w) for w in bcf.nbest(BigramAssocMeasures.pmi, top_n)]
    logging.info("%i bigrams found: %s..." % (len(bigrams), bigrams[:20]))

    pat_gram2 = re.compile('(%s)' % '|'.join(bigrams), re.UNICODE)
    pat_gram3 = re.compile('(%s)' % '|'.join(trigrams), re.UNICODE)

    return pat_gram2, pat_gram3


class CorpusCollocationsTokenizer(object):
    """
    Collocation is a "sequence of words or terms that co-occur more often than would be expected by chance."
     - remove stopwords using gensim.parsing.preprocessing.STOPWORDS.
     - resulting tokens include best_ngrams (brigrams and trigrams).
    """

    def __init__(self, fname):
        self.fname = fname
        logging.info("collecting ngrams from %s" % self.fname)
        # generator of documents; one element = list of words
        documents = (self.split_words(text) for text in iter_material_science_abstracts(self.fname))
        # generator: concatenate (chain) all words into a single sequence, lazily
        words = itertools.chain.from_iterable(documents)
        self.bigrams, self.trigrams = best_ngrams(words)

    def split_words(self, text, stopwords=STOPWORDS):
        """
        Break text into a list of single words. Ignore any token that falls into
        the `stopwords` set.

        """
        return [word
                for word in gensim.utils.tokenize(text, lower=True)
                if word not in STOPWORDS and len(word) > 2]

    def tokenize(self, message):
        """
        Break text (string) into a list of Unicode tokens.

        The resulting tokens can be longer phrases (collocations) too,
        e.g. `new_york`, `real_estate` etc.

        """
        text = u' '.join(self.split_words(message))
        text = re.sub(self.trigrams, lambda match: match.group(0).replace(u' ', u'_'), text)
        text = re.sub(self.bigrams, lambda match: match.group(0).replace(u' ', u'_'), text)
        return text.split()

    def __iter__(self):
        for message in iter_material_science_abstracts(self.fname):
            yield self.tokenize(message)

#collocations_corpus = CorpusMSAbstracts_Collocations('material_science/data/msr-data')


def head(stream, n=10):
    """Convenience fnc: return the first `n` elements of the stream, as plain list."""
    return list(itertools.islice(stream, n))

def best_phrases(document_stream, top_n=10000, prune_at=50000):
    """Return a set of `top_n` most common noun phrases."""
    np_counts = {}
    for docno, doc in enumerate(document_stream):
        # prune out infrequent phrases from time to time, to save RAM.
        # the result may not be completely accurate because of this step
        if docno % 1000 == 0:
            sorted_phrases = sorted(np_counts.iteritems(), key=lambda item: -item[1])
            print(sorted_phrases)
            np_counts = dict(sorted_phrases[:prune_at])
            logging.info("at document #%i, considering %i phrases: %s..." %
                         (docno, len(np_counts), head(sorted_phrases)))

        # how many times have we seen each noun phrase?
        for np in TextBlob(doc).noun_phrases:
            # only consider multi-word NEs where each word contains at least one letter
            if u' ' not in np:
                continue
            # ignore phrases that contain too short/non-alphabetic words
            if all(word.isalpha() and len(word) > 2 for word in np.split()):
                np_counts[np] = np_counts.get(np, 0) + 1

    sorted_phrases = sorted(np_counts, key=lambda np: -np_counts[np])
    return set(head(sorted_phrases, top_n))


class CorpusNERTokenizer(object):
    """
    Named entity recognition (NER) is the task of locating chunks of text that refer to people, locations, organizations etc.
    This tags each word with its part-of-speech (POS) category, and suggests phrases based on chunks of "noun phrases".
     - remove stopwords using gensim.parsing.preprocessing.STOPWORDS.
     - resulting tokens include best_phrases (most common noun phrases).
     - only considers multi-word phrases we detected in the constructor
     - len(part) > 2 and len(token) > 1
    """

    def __init__(self, fname):
        self.fname = fname
        logging.info("collecting entities from %s" % self.fname)
        doc_stream = itertools.islice(iter_material_science_abstracts(self.fname), 10000)
        self.entities = best_phrases(doc_stream)
        logging.info("selected %i entities: %s..." %
                     (len(self.entities), list(self.entities)[:10]))

    def __iter__(self):
        for message in iter_material_science_abstracts(self.fname):
            yield self.tokenize(message)

    def tokenize(self, message, stopwords=STOPWORDS):
        """
        Break text (string) into a list of Unicode tokens.

        The resulting tokens can be longer phrases (named entities) too,
        e.g. `new_york`, `real_estate` etc.

        """
        result = []
        for np in TextBlob(message).noun_phrases:
            if u' ' in np and np not in self.entities:
                # only consider multi-word phrases we detected in the constructor
                continue
            token = u'_'.join(part for part in gensim.utils.tokenize(np) if len(part) > 2)
            if len(token) < 2 or token in stopwords:
                # ignore very short phrases and stop words
                continue
            result.append(token)
        return result

#corpus_ner_only = CorpusMSAbstracts_NER('material_science/data/msr-data')


class CorpusMixedTokenizer(object):
    """
    Includes Named entity recognition (NER) is the task of locating chunks of text that refer to entities.
    This tags each word with its part-of-speech (POS) category, and suggests phrases based on chunks of "noun phrases".
     - remove stopwords using gensim.parsing.preprocessing.STOPWORDS.
     - resulting tokens include best_phrases (most common noun phrases).
     - len(part) > 2 and len(token) > 1
    """

    def __init__(self, fname):
        self.fname = fname
        logging.info("collecting entities from %s" % self.fname)
        doc_stream = itertools.islice(iter_material_science_abstracts(self.fname), 10000)
        self.entities = best_phrases(doc_stream)
        logging.info("selected %i entities: %s..." %
                     (len(self.entities), list(self.entities)[:10]))

    def __iter__(self):
        for message in iter_material_science_abstracts(self.fname):
            yield self.tokenize(message)

    def tokenize(self, message, stopwords=STOPWORDS):
        """
        Break text (string) into a list of Unicode tokens.

        The resulting tokens can be longer phrases (named entities) too,
        e.g. `new_york`, `real_estate` etc.

        """
        result = []
        for np in TextBlob(message).noun_phrases:
            if u' ' in np and np not in self.entities:
                tokens = [word for word in gensim.utils.tokenize(np, lower=True) if word not in STOPWORDS]
                result.extend(tokens)
            else:
                token = u'_'.join(part for part in gensim.utils.tokenize(np) if len(part) > 2)
                if len(token) < 2 or token in stopwords:
                    # ignore very short phrases and stop words
                    continue
                result.append(token)
        return result

if __name__ == "__main__":

    corpus_simple = CorpusSimpleTokenizer('material_science/data/msr-data')
    collocations_corpus = CorpusCollocationsTokenizer('material_science/data/msr-data')
    corpus_ner_only = CorpusNERTokenizer('material_science/data/msr-data')
    corpus_with_ne = CorpusMixedTokenizer('material_science/data/msr-data')

    # Compare results for first abstract

    # First abstract:
    abstract_stream = iter_material_science_abstracts('material_science/data/msr-data')
    print(list(itertools.islice(abstract_stream, 1)))

    # CORPUS SIMPLE
    # print the first tokenized messages
    print(list(itertools.islice(corpus_simple, 1)))

    # CORPUS COLLOCATIONS
    print(list(itertools.islice(collocations_corpus, 1)))

    # CORPUS NER ONLY
    print(head(corpus_ner_only, 1))

    # CORPUS WITH NER
    print(head(corpus_with_ne, 1))
