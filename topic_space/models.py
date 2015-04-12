from __future__ import absolute_import

import os
import time
import subprocess
import logging
import shutil
import webbrowser

import numpy as np

from topik.readers import iter_elastic_query
from topik.tokenizers import EntitiesTokenizer
from topik.vectorizers import CorpusBOW
from topik.models import LDA
from topik.viz import Termite
from topik.utils import to_r_ldavis, generate_csv_output_file


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

BASEDIR = os.path.abspath(os.path.dirname(__file__))

ES_INSTANCE = os.environ['ES_INSTANCE']
ES_INDEX = os.environ['ES_INDEX']

def run_topic_model(field, subfield, output_dir, n_topics, seed=42):

    np.random.seed(seed)

    documents = iter_elastic_query(ES_INSTANCE, ES_INDEX, field, subfield)

    corpus = EntitiesTokenizer(documents)

    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)

    # Create dictionary
    corpus_bow = CorpusBOW(corpus)
    corpus_dict = corpus_bow.save_dict(os.path.join(output_dir, 'corpus.dict'))
    # Serialize and store the corpus
    corpus_file = corpus_bow.serialize(os.path.join(output_dir, 'corpus.mm'))
    # Create LDA model from corpus and dictionary
    lda = LDA(os.path.join(output_dir, 'corpus.mm'), os.path.join(output_dir,'corpus.dict'), n_topics,
              update_every=1, chuncksize=10000, passes=1)
    # Generate the input for the termite plot
    lda.termite_data(os.path.join(output_dir,'termite.csv'))
    # Get termite plot for this model

    termite = Termite(os.path.join(output_dir,'termite.csv'), "Termite Plot")
    termite.plot(os.path.join(output_dir,'termite.html'))

    df_results = generate_csv_output_file(documents, corpus, corpus_bow, lda.model)

    to_r_ldavis(corpus_bow, dir_name=os.path.join(output_dir, 'ldavis'), lda=lda)
    os.environ["LDAVIS_DIR"] = os.path.join(output_dir, 'ldavis')
    try:
        subprocess.call(['Rscript', os.path.join(BASEDIR,'R/runLDAvis.R')])
    except ValueError:
        logging.warning("Unable to run runLDAvis.R")
