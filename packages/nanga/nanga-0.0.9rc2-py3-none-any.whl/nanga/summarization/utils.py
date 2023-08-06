import sys, json, time, math
import pandas as pd


def to_df(data):
    pd_data = []
    n_sentences = 0
    i = 0
    for item in data:
        print(item)
        #for item in content:
        if len(item['sentence'].strip()) > 0:
            pd_data.append({"indice": item['order'], "document": item['sentence'].strip(),
                            "number": i})
            i += 1
            n_sentences += len(item['sentence'].strip().split())
    return pd.DataFrame(pd_data), n_sentences




def add_percent_values(v, vlist):
    if v['number'] in vlist:
        return 1
    return 0


def func(extractive_model, documents, percent):
    docs = documents['document'].tolist()
    num_sentences = [math.ceil(p*len(docs)/100) for p in percent]
    num_sentences_dict = {p: num_sentences[i] for i, p in enumerate(percent)}
    texts_sum, sum_indices = extractive_model(docs, use_first=False, num_sentences=list(set(num_sentences)))
    for p in percent:
        _p = f"percent_{p}"
        documents[_p] = documents.apply(lambda row: add_percent_values(row, sum_indices[num_sentences_dict[p]]), axis=1)
    return documents
