from __future__ import absolute_import

from .dictionaries import iter_corpus

import gensim

import itertools
import logging

import numpy as np
import pandas as pd

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


corpus_simple_mm = gensim.corpora.MmCorpus('material_science/output/simple.mm')
corpus_simple_dict = gensim.corpora.Dictionary.load('material_science/output/simple.dict')
print(corpus_simple_mm)

# Possible models:
# - LDA
# - LSI
# - TF-IDF

lda_model = gensim.models.LdaModel(corpus_simple_mm, num_topics=10, id2word=corpus_simple_dict, passes=4)


# Transforming

# transform text into the bag-of-words space
#bow_vector = id2word_wiki.doc2bow(tokenize(text))
#print([(id2word_wiki[id], count) for id, count in bow_vector])
# transform into LDA space
#lda_vector = lda_model[bow_vector]
#print(lda_vector)
# print the document's single most prominent LDA topic
#print(lda_model.print_topic(max(lda_vector, key=lambda item: item[1])[0]))



# Evaluation

# select top 15 words for each of the 10 LDA topics
top_words = [[word for _, word in lda_model.show_topic(topicno, topn=50)] for topicno in range(lda_model.num_topics)]
print(top_words)

def top_words_termite_input(lda_model):
    top_words = [ lda_model.show_topic(topicno, topn=15) for topicno in range(lda_model.num_topics) ]
    print(top_words)
    count = 1
    for topic in top_words:
        if count == 1:
            df_temp = pd.DataFrame(topic, columns=['weight', 'word'])
            df_temp['topic'] = pd.Series(count, index=df_temp.index)
            df = df_temp
        else:
            df_temp = pd.DataFrame(topic, columns=['weight', 'word'])
            df_temp['topic'] = pd.Series(count, index=df_temp.index)
            df = df.append(df_temp, ignore_index=True)
        count += 1
    return df

df = top_words_termite_input(lda_model)
df.to_csv('material_science/output/simple_termite.csv')
# evaluate on 1k documents **not** used in LDA training
doc_stream = (tokens for tokens in iter_corpus(corpus_simple_mm))  # generator
test_docs = list(itertools.islice(doc_stream, 8000, 9000))

def intra_inter(model, test_docs, num_pairs=10000):
    # split each test document into two halves and compute topics for each half
    part1 = [model[corpus_simple_dict.doc2bow(tokens[: len(tokens) / 2])] for tokens in test_docs]
    part2 = [model[corpus_simple_dict.doc2bow(tokens[len(tokens) / 2 :])] for tokens in test_docs]

    # print computed similarities (uses cossim)
    print("average cosine similarity between corresponding parts (higher is better):")
    print(np.mean([gensim.matutils.cossim(p1, p2) for p1, p2 in zip(part1, part2)]))

    random_pairs = np.random.randint(0, len(test_docs), size=(num_pairs, 2))
    print("average cosine similarity between 10,000 random parts (lower is better):")
    print(np.mean([gensim.matutils.cossim(part1[i[0]], part2[i[1]]) for i in random_pairs]))
