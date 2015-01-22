import pandas as pd
import json


def read_file_msr_data(filename):
    list_of_dicts = []
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            try:
                list_of_dicts.append(json.loads(line))
            except ValueError:
                print("Unable to process line:\n\t", line)
    return pd.DataFrame(list_of_dicts)


def stopwords_set(filename):
    stopwords = set()
    with open(filename, 'r') as f:
        for line in f.readlines():
            for word in line.split():
                stopwords.add(word)
    return stopwords
