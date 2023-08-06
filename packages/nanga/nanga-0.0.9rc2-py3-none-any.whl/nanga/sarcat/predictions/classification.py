# @copyright  Copyright (c) 2018-2020 Opscidia

import logging, os, time, numpy as np
from sarcat.models.legacy.modules import load_model
from sarcat.models.legacy.utils import get_mcat_dict
from sarcat.predictions.utils import data_loader
from threading import Thread
import math
import multiprocessing
import random, time
import threading



logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.ERROR)

class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            print('[%s]' % self.name, end=' ')
        print('Elapsed: %s' % (time.time() - self.tstart))

class Predictor(object):
    """
    
    """
    
    def __init__(self, model_path=None):
        
        self.model = None
        if model_path is not None and not os.path.isfile(model_path):
            logging.warning(f'Model path {model_path} does not exits. You can use  _load_model function to load one model before predicting')
            self.model_path = None
        elif model_path is None:
            self.model_path = None
            logging.warning(f'You have to use _load_model function to load one model before predicting.')
        else:
            self.model_path = model_path
            self.model, _ = self._load_moodel(self.model_path)
        
        self.categories = get_mcat_dict()
       
            
            
            
    def _load_moodel(self, model_path=None):
        """
        Load model weights given a path.
        :param model_path: path to model.
        """
#         start = time.process_time()
        return load_model(self.model_path)
#         print(f'Model loading: {time.process_time() - start} sec')
        
    
    def _get_category(self, label):
        if label in self.categories:
            return self.categories[label]
        logging.wargning(f'{label} is unknown label.')
        return None
    
            
    def get_labels_probs(self, title=None, abstract=None, n=1):
        """
        Given a title and an abstract, get the category with probabilities.
        """
        #print('get_labels_probs.len:', len(title), len(abstract))
        
        if title is None or abstract is None:
            logging.error("Title or abstract must not be None.")
            return {"categories": None, "confidences":None}
        preds = self.model.predict(title, abstract)
        labels = []
        confidences = []
        if n>2 :
            n = 2
            
        logging.info(f'Predictions return: {preds}')
        for i in range(0,n):
            labels.append(self._get_category(preds[i][0]))
            confidences.append(preds[i][1])
            
            
        return {"categories": labels, "confidences":confidences}
    
    def get_labels_probs_single(self, data=None, n=1):
        """
        Given a title and an abstract, get the category with probabilities.
        """
        
        if data is None or len(data) < 2:
            logging.error("List containing title and abstract must not be None and must contain a tuple of title and abstract.")
            return {"categories": None, "confidences":None}
        title = data[0]
        abstract = data[0]
        preds = self.model.predict(title, abstract)
        labels = []
        confidences = []
        if n>2 :
            n = 2
            
        logging.debug(f'Predictions return: {preds}')
        for i in range(0,n):
            labels.append(self._get_category(preds[i][0]))
            confidences.append(preds[i][1])
            
            
        return {"categories": labels, "confidences":confidences}
    
    
    @staticmethod
    def tranform_input(input_):
        """
        Check if input is an instance of list and transform it to string
        
        :param input_: str or list
        
        
        """
        if isinstance(input_, list) and len(input_) > 0:
            input_ = input_[0]
        elif isinstance(input_, list) and len(input_) == 0:
            input_ = ""
        
        return input_
    
    
    def get_labels_probs_from_es(self, ids=None, title=None, abstract=None, using_es_index=False, n=1):
        """
        Given a title and an abstract, get the category with probabilities.
        """
        
        if using_es_index:
            if title is None or abstract is None or ids is None:
                logging.error("Title or abstract must not be None.")
                return {"categories": None, "confidences":None, '_id':None}
        else:
            
            title = Predictor.tranform_input(title)
            abstract = Predictor.tranform_input(abstract)
            preds = self.model.predict(title, abstract)
            labels = []
            confidences = []
            indexes = []
            if n>2 :
                n = 2
                
    #         logging.info(f'Predictions return: {preds}')
            for i in range(0,n):
                labels.append(self._get_category(preds[i][0]))
                confidences.append(preds[i][1])
            
#         return (ids, labels[0], confidences[0])
        if using_es_index:
            return {"_id": ids, "categories": labels, "confidences":confidences}
        else:
            return {"categories": labels, "confidences":confidences}
    
    
    
        
        
        
    def get_labels(self, title=None, abstract=None, n=1):
        """
        Given a title and an abstract, get the category.
        """
        
        if title is None or abstract is None:
            logging.error("Title or abstract must not be None.")
            return {"categories": None, "confidences":None}
        preds = self.model.predict(title, abstract)
        labels = []
        confidences = []
        if n>2 :
            n = 2
        for i in range(1,n):
            labels.append(self._get_category(preds[i][0]))
            confidences.append(preds[i][1])
              
        return {"categories": labels, "confidences":confidences}
        
        
            
            
    
class Predictors(Predictor):
    
    def __init__(self, model_path):
        super().__init__(model_path)
        
        
        
    def from_ES(self, titles_abstracts:list = [], batch_size:int = 16, temporary_file:str=None, using_es_index=False):
        """
        Predictions from a list of tuples containing article id, titles and abstracts.
        :param titles_abstracts: list of tuples
        :param batch_size: batch size
        :param temporary_file: temporary filename to store the results.
        """
        if isinstance(titles_abstracts, list):
            data = self.batchify(titles_abstracts, batch_size)
            results = np.array([], dtype='object')
            for i, articles in enumerate(data):
                start = time.process_time()
                if using_es_index:
                    res = np.array(list(map(lambda d: self.get_labels_probs_from_es(ids=d[0], title=d[1], abstract=d[2]), articles)))
                else:
                    res = np.array(list(map(lambda d: self.get_labels_probs_from_es(title=d[0], abstract=d[1]), articles)))
                results = np.append(results, res)
                del res
                print(f'Batch predictions: {i} - Executime time: {time.process_time() - start} sec ') 
            return results 
        
    def from_df(self, df, batch_size:int = 16):
        """
        Predictions from a list of tuples containing article id, titles and abstracts.
        :param titles_abstracts: list of tuples
        :param batch_size: batch size
        :param temporary_file: temporary filename to store the results.
        """
        if 'title' in df.columns and 'abstract' in df.columns:
            titles = df['title'].values
            abstracts = df['abstract'].values
            results = self.from_lists(titles.tolist(), abstracts.tolist(), batch_size)
            df['categories'] = [p['categories'] for p in results]
            df['confidences'] = [p['confidences'] for p in results]
            return df
        
            
   
        
        
    def from_lists(self, titles:list = [], abstracts:list = [], batch_size:int = 16):
        """
        Predictions from a list of  titles and a list of abstracts.
        :param titles: list of titles
        :param abstracts: list of abstracts
        :param batch_size: batch size
        :param temporary_file: temporary filename to store the results.
        """
        if isinstance(titles, list) and isinstance(abstracts, list):
            assert len(titles) == len(abstracts), "len of titles list must be the same to len of abstracts"
            ntotal = len(titles)
            titles = self.batchify(titles, batch_size)
            abstracts = self.batchify(abstracts, batch_size)
            results = np.array([], dtype='object')
            atime = 0
            tbatch = 0
            for i, articles in enumerate(zip(titles, abstracts)):
                _titles = articles[0]
                _abstracts = articles[1]
                start = time.process_time()
                tbatch += 1
                res = np.array(list(map(lambda t, v: self.get_labels_probs(title=t, abstract=v), _titles, _abstracts)))
                print(f'Batch predictions: {i} - Executime time: {time.process_time() - start} sec ') 
                atime += time.process_time() - start
                results = np.append(results, res)
                del res
            if tbatch > 0:
                print(f'Each batch has taken: {atime/tbatch} sec')
            else:
                print(f'Each batch has taken: {tbatch} sec')
            return results 
       
        
        
    def from_lists_(self, titles:list = [], abstracts:list = [], batch_size:int = 16):
        """
        Predictions from a list of  titles and a list of abstracts.
        :param titles: list of titles
        :param abstracts: list of abstracts
        :param batch_size: batch size
        :param temporary_file: temporary filename to store the results.
        """
        if isinstance(titles, list) and isinstance(abstracts, list):
            assert len(titles) == len(abstracts), "len of titles list must be the same to len of abstracts"
            ntotal = len(titles)
            data = [(t,v) for t, v in zip(titles, abstracts)]
            data = self.batchify(data, batch_size)
            results = np.array([], dtype='object')
            atime = 0
            for i, d in enumerate(data):
                start = time.process_time()
                numparallel = 2
                with Timer('mp %s' % numparallel):
                    res = self.mul_process(d, numparallel)
                print(f'Batch predictions: {i} - Executime time: {time.process_time() - start} sec ') 
                atime += time.process_time() - start
                results = np.append(results, res)
                del res
            print(f'Each batch has taken: {atime/(ntotal//batch_size)} sec')
               
               
            #titles = self.batchify(titles, batch_size)
            #abstracts = self.batchify(abstracts, batch_size)
            #results = np.array([], dtype='object')
            #atime = 0
            #for i, articles in enumerate(zip(titles, abstracts)):
                #_titles = articles[0]
                #_abstracts = articles[1]
                #start = time.process_time()
                #res = np.array(list(map(lambda t, v: self.get_labels_probs(title=t, abstract=v), _titles, _abstracts)))
                #print(f'Batch predictions: {i} - Executime time: {time.process_time() - start} sec ') 
                #atime += time.process_time() - start
                #results = np.append(results, res)
                #del res
            #print(f'Each batch has taken: {atime/(ntotal//batch_size)} sec')
            return results 
            
           
         
            
    def batchify(self, data, bz=16):
        ntotal = len(data)
        for nbatch in range(0, ntotal, bz):
            yield data[nbatch:min(nbatch+bz, ntotal)]
            
    def batchify_titles_abstracts(self, titles:list=None, abstracts:list=None, bz=16):
        """
        Batchify data using titles and abstracts separately. 
        :param titles: list of titles
        :param abstracts: list of abstracts
        :param batch_size: batch size
        """
        assert len(titles) == len(abstracts), "len of titles list must be the same to len of abstracts"
        ntotal = len(titles)
        for nbatch in range(0, ntotal, bz):
            min_batch = min(nbatch+bz, ntotal)
            yield titles[nbatch:min_batch]
            yield abstracts[nbatch:min_batch]
            
    
    
    def create_bulk_request(self, n, processor):
        print(processor.process(n))
        
        
    def mul_process(self, data, nprocs):
        def worker(data, out_q):
            """ The worker function, invoked in a process. 'nums' is a
                list of numbers to factor. The results are placed in
                a dictionary that's pushed to a queue.
            """
            outdict = {}
            for i, d in enumerate(data):
                outdict[i] = self.get_labels_probs_single(d)
            out_q.put(outdict)

        # Each process will get 'chunksize' nums and a queue to put his out
        # dict into
        out_q = multiprocessing.Queue()
        chunksize = int(math.ceil(len(data) / float(nprocs)))
        procs = []

        for i in range(nprocs):
            p = multiprocessing.Process(
                    target=worker,
                    args=(data[chunksize * i:chunksize * (i + 1)],
                        out_q))
            procs.append(p)
            p.start()

        # Collect all results into a single result dict. We know how many dicts
        # with results to expect.
        resultdict = {}
        for i in range(nprocs):
            print('>>>', i, resultdict)
            resultdict.update(out_q.get())

        # Wait for all worker processes to finish
        for p in procs:
            p.join()

        return resultdict
