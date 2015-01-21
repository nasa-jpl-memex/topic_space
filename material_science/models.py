from __future__ import absolute_import, division, print_function

import string

from .utils import read_file_msr_data, stopwords_set

import logging
from gensim import corpora, models, similarities

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

MSR_DATA_FILE = "material_science/data/msr-data"


# Dictionaries
# We can have different dictionaries:
# 1 - All words in the corpus minus stop list and words that appear only once

# STOPWORDS LIST
# https://code.google.com/p/stop-words/

STOPWORDS_FILE = "material_science/data/stop-words_english_6_en.txt"

DICTIONARY = 'material_science/output/msr_corpus.dict'

def create_dictionary(input_data, stopwords_file, output_file):
    msr_data = read_file_msr_data(input_data)
    stopwords = stopwords_set(stopwords_file)
    documents = msr_data.abstract

    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    texts = [[word.lower() for word in document.translate(remove_punctuation_map).split() if word not in stopwords]
                 for document in documents]

    all_tokens = sum(texts, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    word_list = [[word for word in text if word not in tokens_once]
             for text in texts]

    dictionary = corpora.Dictionary(word_list)
    dictionary.save(output_file) # store the dictionary, for future reference
    print(dictionary)
    return dictionary


dictionary_1 = create_dictionary(MSR_DATA_FILE, STOPWORDS_FILE, DICTIONARY)

#Dictionary(175991 unique tokens: [u'llactic', u'005\xba', u'y004\u2013006', u'27\xb0', u'mdbt']...)

# 2 - Dictionary of material science terms

# 3 - Dictionary of chemical terms


# Different models

# - Term frequency
class MSAbstractsCorpus(object):
    def __init__(self, input_data, stopwords_file, dictionary):
        self.input_data = input_data
        self.stopwords_file = stopwords_file
        self.dictionary = dictionary

    def __iter__(self):
        dictio = corpora.Dictionary.load(self.dictionary)
        documents = read_file_msr_data(self.input_data).abstract
        for document in documents:
            # assume there's one document per line, tokens separated by whitespace
            yield dictio.doc2bow(document.lower().split())


corpus = MSAbstractsCorpus(MSR_DATA_FILE, STOPWORDS_FILE, DICTIONARY)

#for vector in corpus:
#    print(vector)

# - TF-IDF

# - LSA/LSI

# - LDA

# - HDP