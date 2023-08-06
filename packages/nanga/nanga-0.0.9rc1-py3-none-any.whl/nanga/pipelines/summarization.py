from nanga.summarization import BertSummarizer
from nanga.summarization.inference import extractive


class SummarizationPipeline():
    """
    Summarizer pipeline
    """


    def __init__(self, model_name):
        self.model = BertSummarizer(model=model_name)


    def __call__(self,
                 body: [str, list],
                 percent: list):
        return extractive(self.model, body, percent)





