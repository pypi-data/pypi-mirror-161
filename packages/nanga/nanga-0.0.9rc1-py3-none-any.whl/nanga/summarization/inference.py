import sys, json, time, math
from joblib import Parallel, delayed
import multiprocessing, threading
from .utils import func, to_df



def df_summarizer(model, documents, percent):
    """
    """
    thread1 = threading.Thread(target=func, args=(model, documents, percent))
    thread1.start()
    thread1.join()
    return documents

def extractive(model,
               documents,
               percent):
    """
    Apply extractive summarization.
    :param data: Content list of sentences.
    :param percent: The percent of sentences to return.
    :return: A tuple of summarized sentences and embeddings
    """
    documents = df_summarizer(model, documents, percent)
    return documents
