from __future__ import absolute_import, division, print_function

import string

from .utils import read_file_msr_data, stopwords_set

import logging
from gensim import corpora, models, similarities

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

MSR_DATA_FILE = "material_science/data/msr-data"

msr_data = read_file_msr_data(MSR_DATA_FILE)


# Dictionaries
# We can have different dictionaries:
# 1 - All words in the corpus minus stop list and words that appear only once

# STOPWORDS LIST
# https://code.google.com/p/stop-words/

STOPWORDS_FILE = "material_science/data/stop-words_english_6_en.txt"
stopwords = stopwords_set(STOPWORDS_FILE)

documents = msr_data.abstract

remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
word_list = [[word.lower() for word in document.translate(remove_punctuation_map).split() if word not in stopwords]
             for document in documents]

dict = corpora.Dictionary(word_list)
dict.save('material_science/output/msr_corpus.dict') # store the dictionary, for future reference
print(dict)

#Dictionary(175991 unique tokens: [u'llactic', u'005\xba', u'y004\u2013006', u'27\xb0', u'mdbt']...)

# 2 - Dictionary of material science terms

# 3 - Dictionary of chemical terms


#class MSAbstractsCorpus(object):
#    def __iter__(self):
#        for line in open('mycorpus.txt'):
#            # assume there's one document per line, tokens separated by whitespace
#            yield dictionary.doc2bow(line.lower().split())


# Different models

# - Term frequency

# - TF-IDF

# - LSA/LSI

# - LDA

# - HDP