from .summarization import SummarizationPipeline
from .sarcat import SarcatPipeline
from nanga.utils import logger

pipelines = {'summarization': SummarizationPipeline,
             'sarcat': SarcatPipeline,
            }


class Pipeline(object):
    """
    Base class to use pipeline object
    """

    def __init__(self,
                 task: str,
                 **kwargs):
        if not task in pipelines:
            logger.error(f"{task} not recognized.")

        self.pipeline = pipelines[task](**kwargs)


    def __call__(self,
                 **kwargs):
        return self.pipeline(**kwargs)


