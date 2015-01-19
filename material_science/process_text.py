"""Visualizations of the material science research files"""

import json
import os
import random

import numpy as np
import pandas as pd
import pattern.vector as pv
from wordcloud import WordCloud

import bokeh.plotting as plt


FONT_PATH = "DejaVuSans.ttf"
DATA_FILE = "msr-data"
STOPWORD_FILE = "stopwords_wordnet.txt"


def make_output_dir(dir_name="output"):
    try:
        os.mkdir(dir_name)
    except OSError:
        pass


def read_file():
    list_of_dicts = []
    with open(DATA_FILE, 'r') as fp:
        for line in fp.readlines():
            try:
                list_of_dicts.append(json.loads(line))
            except ValueError:
                print("Unable to process line:\n\t", line)
    return pd.DataFrame(list_of_dicts)


def read_sample(n=10):
    df = read_file()
    rows = random.sample(df.index, n)
    return df.ix[rows]


def get_abstracts_by_year(df):
    abstracts = {}
    grouped = df.groupby('year')
    for year, pks in grouped.groups.iteritems():
        abstracts[year] = df.loc[pks]
    return abstracts


def create_models(group):
    docs = [pv.Document(item, threshold=1) for item in group]
    return pv.Model(docs, weight=pv.TFIDF)


def get_models_by_year(df):
    return df[['year', 'abstract']].groupby('year').apply(create_models)


def get_clusters_by_year(df, k=5):
    return get_models_by_year(df).apply(lambda x: x.cluster(pv.KMEANS, k=k))


def lsa_apply(df):
    m = pv.Model([pv.Document(a) for a in df['abstract']], weight=pv.TFIDF)
    return m.reduce(2)


def get_lsa_by_year(df):
    return df[['year', 'abstract']].groupby('year').apply(lsa_apply)


def generate_annual_wordclouds(df, field):
    abstract_series = df[["year", field]].groupby("year").agg(np.sum)
    wordclouds = []
    for year in abstract_series.index:
        abstract = abstract_series.ix[year][field]
        wordclouds.append((year, WordCloud(font_path=FONT_PATH).generate(abstract)))
    return wordclouds


def generate_word_cloud_image(text, filename="output/wordcloud.jpg"):
    wordcloud = WordCloud(font_path=FONT_PATH).generate(text)
    wordcloud.to_image().save(filename, "JPEG")


def generate_annual_wordcloud_images(df, field):
    make_output_dir(os.path.join("output", field))
    wcs = generate_annual_wordclouds(df, field)
    for year, wordcloud in wcs:
        wordcloud.to_image().save(os.path.join("output", field, year+".jpg"), "JPEG")


def wordclouds_to_bokeh(wordclouds):
    plt.output_file("wordclouds.html", title="Wordclouds of Abstracts 1by Year")
    images = [w.to_image() for y, w in wordclouds]
    p = plt.figure(x_range=[0, 10], y_range=[0, 10])
    # XXX: Need to figure out how to put images in
    p.image(image=images, x=range(len(images)), y=[0]*len(images), dw=[10]*len(images), dh=[10]*len(images), palette="Spectral11")

    plt.show(p)


def interesting_words(lsa, n=3):
    lsa_df = pd.DataFrame.from_dict(lsa.concepts)
    res = []
    for row, series in lsa_df.iterrows():
        series.sort(ascending=False)
        print series[0]
        if series[0] <= 1e-8:
            print "in pass"
            continue
    res_df = pd.DataFrame(res).transpose()
    res_df.fillna(0, inplace=True)
    return res_df


def interesting_words_1(lsa, n=3):
    lsa_df = pd.DataFrame.from_dict(lsa.concepts)
    res = []
    for row, series in lsa_df.iterrows():
        s = sorted([(abs(y), x) for x, y in series.iterkv()], reverse=True)
        res.extend([x for y,x in s[:n]])
    return set(res)


def to_str(wordlist):
    for a in wordlist:
        try:
            yield str(a)
        except UnicodeEncodeError:
            pass


def bokeh_lsa(year, df):
    plt.output_file('output/lsa/'+str(year)+'.html')

    topics = [str(a) for a in df.columns]
    words = list(to_str(df.index))
    p = plt.figure(x_range=topics, y_range=words,
           plot_width=800, plot_height=600,
           title=year, tools='resize, save')

    plot_sizes = []
    plot_topics = []
    plot_words = []
    print df
    for word, coeff in df.iterrows():
        for n, c in enumerate(coeff):
            if c > 0:
                plot_sizes.append(c)
                plot_topics.append(str(n))
                plot_words.append(word)
    if len(plot_sizes) == 0:
        return
    max_size = np.max(plot_sizes)
    plot_sizes = [int(a/max_size * 75) + 25 for a in plot_sizes]

    print plot_sizes, plot_words, plot_topics

    p.circle(x=plot_topics, y=plot_words, size=plot_sizes, fill_alpha=0.6)
    plt.show(p)

    return plt.curplot()


def create_Kane_csv(df):
    """
    CSV Columns:
    title, abstract, url, year, author
    """
    
    df.to_csv("msr_data.csv", columns=["title", "abstract", "url", "year", "authors"], encoding="utf-8")


def main_wordclouds():
    df = read_file()
    generate_annual_wordcloud_images(df, "abstract")
    generate_annual_wordcloud_images(df, "title")


def main_example():
    df = read_sample(100)
    #df = read_file()
    lsas = get_lsa_by_year(df)
    lsa_df = pd.DataFrame.from_dict({'year' : lsas.index,
                                     'lsa_terms' : [" ".join(a.terms) for a in lsas]})
    print lsa_df
    generate_annual_wordcloud_images(lsa_df, 'lsa_terms')
    #lsa_df = interesting_words(lsa)
    #p = bokeh_lsa(year, lsa_df)
    return


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


if __name__ == "__main__":
    #main_example()
    pass
