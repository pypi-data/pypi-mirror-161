import sys
from typing import List, Optional, Union, Tuple, Dict
import numpy as np
from functools import partial
from nanga.summarization import BertEmbedding
from nanga.summarization.core.texts import SentenceHandler
from nanga.summarization.core.clusters import ClusterFeatures
from transformers import (AlbertModel, AlbertTokenizer, BertModel,
                          BertTokenizer, DistilBertModel, DistilBertTokenizer,
                          PreTrainedModel, PreTrainedTokenizer, XLMModel,
                          XLMTokenizer, XLNetModel, XLNetTokenizer,
                          AutoConfig, AutoTokenizer, AutoModel)




class BertSummarizer(object):


    def __init__(self,
                model: Optional[str] = 'bert-large-uncased',
                custom_model: PreTrainedModel = None,
                custom_tokenizer: PreTrainedTokenizer = None,
                hidden: Union[List[int], int] = -2,
                reduce_option: str = 'mean',
                sentence_handler: SentenceHandler = SentenceHandler(),
                random_state: int = 12345,
                hidden_concat: bool = False,
                gpu_id: int = 0,
            ):
        model = BertEmbedding(model, custom_model, custom_tokenizer, gpu_id)
        self.model = partial(model, hidden=hidden, reduce_option=reduce_option, hidden_concat=hidden_concat)
        self.sentence_handler = sentence_handler
        self.random_state = random_state



    def cluster_runner(
        self,
        sentences: List[str],
        ratio: float = 0.2,
        algorithm: str = 'kmeans',
        use_first: bool = True,
        num_sentences: [int, list] = 3,
    ) -> Tuple[List[str], np.ndarray]:
        """
        Runs the cluster algorithm based on the hidden state. Returns both the embeddings and sentences.
        :param sentences: Content list of sentences.
        :param ratio: The ratio to use for clustering.
        :param algorithm: Type of algorithm to use for clustering.
        :param use_first: Return the first sentence in the output (helpful for news stories, etc).
        :param num_sentences: Number of sentences to use for summarization.
        :return: A tuple of summarized sentences and embeddings
        """
        first_embedding = None
        hidden = self.model(sentences)


        if use_first:
            if isinstance(num_sentences, list):
                num_sentences = [n - 1 for n in num_sentences] if num_sentences else num_sentences
            else:
                num_sentences = num_sentences - 1 if num_sentences else num_sentences

            if len(sentences) <= 1:
                return sentences, hidden

            first_embedding = hidden[0, :]
            hidden = hidden[1:, :]

        summary_sentence_indices, n_clusters = ClusterFeatures(
            hidden, algorithm, random_state=self.random_state).cluster(ratio, num_sentences)

        print('N_clusters: ', n_clusters, summary_sentence_indices)
        ssi = summary_sentence_indices

        if use_first:
            if  isinstance(summary_sentence_indices, dict):
                summary_sentence_indices_dict = {}
                for k, sents in summary_sentence_indices.items():
                    summary_sentence_indices_dict[k+1] = BertSummarizer._summary_sentences_indices(sents)
                summary_sentence_indices = summary_sentence_indices_dict
            else:
                summary_sentence_indices = BertSummarizer._summary_sentences_indices(sents)


        if isinstance(summary_sentence_indices, dict):
            sentences = {k: [sentences[j] for j in sents] for k, sents in summary_sentence_indices.items()}
        else:
            sentences = [sentences[j] for j in summary_sentence_indices]

        return sentences, ssi

    @staticmethod
    def _summary_sentences_indices(summary_sentence_indices):
        if summary_sentence_indices:
            # adjust for the first sentence to the right.
            summary_sentence_indices = [i + 1 for i in summary_sentence_indices]
            summary_sentence_indices.insert(0, 0)
        else:
            summary_sentence_indices.append(0)
        return summary_sentence_indices

    def run(
        self,
        body: [str, list],
        ratio: float = 0.2,
        min_length: int = 0,
        max_length: int = 6000,
        use_first: bool = True,
        algorithm: str = 'kmeans',
        num_sentences: [int, list] = None,
        return_as_list: bool = False,
    ) -> Union[List, str]:
        """
        Preprocesses the sentences, runs the clusters to find the centroids, then combines the sentences.
        :param body: The raw string body to process
        :param ratio: Ratio of sentences to use
        :param min_length: Minimum length of sentence candidates to utilize for the summary.
        :param max_length: Maximum length of sentence candidates to utilize for the summary
        :param use_first: Whether or not to use the first sentence
        :param algorithm: Which clustering algorithm to use. (kmeans, gmm)
        :param num_sentences: Number of sentences to use (overrides ratio).
        :param return_as_list: Whether or not to return sentences as list.
        :return: A summary sentence
        """
        if isinstance(body, str):
            sentences = self.sentence_handler(body, min_length, max_length)
        else:
            sentences = body
        print('###', sentences)


        if sentences:
            # sentences, _ = self.cluster_runner(sentences, ratio, algorithm, use_first, num_sentences)
            sentences, summary_sentence_indices = self.cluster_runner(sentences, ratio, algorithm, use_first, num_sentences)
            print('***> ', sentences, summary_sentence_indices)

        if return_as_list:
            return sentences, summary_sentence_indices
        elif isinstance(sentences, dict):
            return {k: ' '.join(sentence) for k, sentence in sentences.items()}, summary_sentence_indices
        else:
            return ' '.join(sentences), summary_sentence_indices


    def __call__(
        self,
        body: [str, list],
        ratio: float = 0.2,
        min_length: int = 0,
        max_length: int = 6000,
        use_first: bool = True,
        algorithm: str = 'kmeans',
        num_sentences: [int, list] = None,
        return_as_list: bool = False,
    ) -> str:
        """
        (utility that wraps around the run function)
        Preprocesses the sentences, runs the clusters to find the centroids, then combines the sentences.
        :param body: The raw string body to process.
        :param ratio: Ratio of sentences to use.
        :param min_length: Minimum length of sentence candidates to utilize for the summary.
        :param max_length: Maximum length of sentence candidates to utilize for the summary.
        :param use_first: Whether or not to use the first sentence.
        :param algorithm: Which clustering algorithm to use. (kmeans, gmm)
        :param num_sentences: Number of sentences to use (overrides ratio).
        :param return_as_list: Whether or not to return sentences as list.
        :return: A summary sentence.
        """
        return self.run(body, ratio, min_length, max_length,
                        use_first, algorithm, num_sentences, return_as_list)
