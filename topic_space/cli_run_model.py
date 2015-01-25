from __future__ import absolute_import

from topic_space.preprocessing import (CorpusCollocationsTokenizer, CorpusMixedTokenizer,
                                       CorpusNERTokenizer, CorpusSimpleTokenizer)

from topic_space.vector_space import CorpusDict, CorpusBOW
from topic_space.models import LDA
from topic_space.visualizations import Termite

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="TOPIC SPACE")

    parser.add_argument("-d", "--data", required=True, action = "store", help="Path to input file for topic modeling ")
    parser.add_argument("-n", "--name", action="store", help="Topic modeling name", default="topic_model")
    parser.add_argument("-p", "--preprocessing", action = "store",
                        help="Tokenize method to use id: "
                             "1-Simple, 2-Collocations, 3-Name Entity Recognition, 4-Mix")
    parser.add_argument("-t", "--topics", action = "store",
                       help="Number of topics to use in LDA")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    ntopics = int(args.topics)
    if args.data:
        if args.preprocessing == "1":
            corpus = CorpusSimpleTokenizer(args.data)
        elif args.preprocessing == "2" :
            corpus = CorpusCollocationsTokenizer(args.data)
        elif args.preprocessing == "3":
            corpus = CorpusNERTokenizer(args.data)
        elif args.preprocessing == "4":
            corpus = CorpusMixedTokenizer(args.data)
        else:
            print("Processing value invalid, using 1-Simple by default")
            corpus = CorpusSimpleTokenizer(args.data)

        # Create dictionary
        name = args.name
        corpus_dict = CorpusDict(corpus, '%s.dict' % name).create()
        # Transform corpus to bag-of-words vector space
        corpus_bow = CorpusBOW(corpus, corpus_dict)
        # Serialize and store the corpus
        corpus_bow.serialize('%s.mm' % name)
        # Create LDA model from corpus and dictionary
        lda = LDA('%s.mm' % name, '%s.dict' % name, ntopics)
        # Generate the input for the termite plot
        lda.generate_termite_input('%s_termite.csv' % name)
        # Get termite plot for this model
        termite = Termite('%s_termite.csv' % name, "Termite Plot for %s" % name)
        termite.plot('%s_termite.html' %name)