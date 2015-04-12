"""Visualizations of the material science research files"""

import cPickle
import os
import os.path

import pandas as pd
import pattern.vector as pv
from wordcloud import WordCloud

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

from config import ELASTICSEARCH_HOST, ELASTICSEARCH_INDEX

FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DejaVuSans.ttf")
PKL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs_by_year.pkl")



def make_output_dir(dir_name="output"):
    try:
        os.mkdir(dir_name)
    except OSError:
        pass


#USED
def read_elasticsearch():
    es = Elasticsearch([ELASTICSEARCH_HOST])
    years = []
    abstracts = []
    if es.indices.exists(ELASTICSEARCH_INDEX):
        query = {"query": {"match_all": {}}}
        scanner = scan(es, index=ELASTICSEARCH_INDEX, query=query, size=1000)
        for res in scanner:
            try:
                res = res["_source"]
                year = res["dateCreated"].split('-')[0]
                abstract = res["hasAbstractPart"]["text"]
                years.append(year)
                abstracts.append(abstract)
            except KeyError:
                pass
    else:
        raise RuntimeError("Could not connect to ELASTICSEARCH_INDEX: %s" % ELASTICSEARCH_INDEX)
    return pd.DataFrame({"year": years, "abstract": abstracts})


def lsa_apply(df):
    print("Building model")
    m = pv.Model([pv.Document(a) for a in df['abstract']], weight=pv.TFIDF)
    print("Returning reduction")
    return m.reduce(2)


def get_lsa_by_year(df):
    return df[['year', 'abstract']].groupby('year').apply(lsa_apply)


def get_word_cloud_image(text):
    wordcloud = WordCloud(font_path=FONT_PATH).generate(text)
    return wordcloud.to_image()


def generate_word_cloud_image(text, filename="output/wordcloud.jpg"):
    get_word_cloud_image().save(filename, "JPEG")


def interesting_words_1(lsa, n=3):
    lsa_df = pd.DataFrame.from_dict(lsa.concepts)
    res = []
    for row, series in lsa_df.iterrows():
        s = sorted([(abs(y), x) for x, y in series.iterkv()], reverse=True)
        res.extend([x for y,x in s[:n]])
    return set(res)


def get_docs_by_year():
    print("reading data")
    df = read_elasticsearch()

    print("computing lsa")
    lsas = get_lsa_by_year(df)
    print("concating texts")
    texts = df[['year', 'abstract']].groupby('year').sum()
    counts = df[['year', 'abstract']].groupby('year').count()
    print("building dataframe")
    doc_dicts = []
    for year, lsa in lsas.iterkv():
        text = texts.ix[year]['abstract']
        words = interesting_words_1(lsa, 100)
        lsa_terms = set(words)
        processed_texts = " ".join([w for w in text.split() if w in lsa_terms])
        doc_dicts.append({"year": year,
                          "lsa_abs": processed_texts,
                          "num_docs": counts.ix[year]['abstract'],
                         })
    doc_df = pd.DataFrame(doc_dicts)
    return doc_df


def main_msr_wordclouds():
    make_output_dir("output/lsa_abs")
    doc_df = get_docs_by_year()
    for row, (abs, year) in doc_df.iterrows():
        generate_word_cloud_image(abs, "output/lsa_abs/"+year+".jpg")


def read_court_files(folder_path):
    import glob
    files = glob.glob(folder_path + "/*")
    texts = []
    for name in files: # 'file' is a builtin type, 'name' is a less-ambiguous variable name.
        try:
            with open(name) as f: # No need to specify 'r': this is the default.
                texts.append(f.read())
        except IOError as exc:
            pass
    return texts


def get_lsa(texts):
    docs = [pv.Document(a) for a in texts]
    model = pv.Model(docs, weight=pv.TFIDF)
    lsa = model.reduce(2)
    return lsa


def flatten_list(l):
    return [item for sublist in l for item in sublist]


def main_court_lsa_words():
    texts = read_court_files("court")
    lsa_terms = " ".join(get_lsa(texts).terms)
    generate_word_cloud_image(lsa_terms, "output/court_doc")


def main_court_minus_lsa_words():
    texts = read_court_files("court")
    words = interesting_words_1(get_lsa(texts), 100)
    lsa_terms = set(words)
    processed_texts = [w for w in flatten_list([t.split() for t in texts]) if w in lsa_terms]
    doc = " ".join(processed_texts)
    generate_word_cloud_image(doc, "output/court_doc.jpg")

def test_wordcloud():
    generate_word_cloud_image("ABC ABC ABD ABD", "test.jpg")


def create_docs():
    df = get_docs_by_year()
    cPickle.dump(df, open(PKL_FILE, 'w'), protocol=2)


def load_docs():
    if not os.path.exists(PKL_FILE):
        create_docs()
    return cPickle.load(open(PKL_FILE))

if __name__ == "__main__":
    #main_example()
    #test_wordcloud()
    create_docs()
