# WIP

# Evaluation of models

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
