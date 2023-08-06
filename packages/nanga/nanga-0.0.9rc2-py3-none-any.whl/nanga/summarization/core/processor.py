from typing import Callable, List, Optional, Tuple, Union
import numpy as np
from core.texts import SentenceHandler



class SummaryProcessor:
    """
    """

    def __init__(self,
                 model: Callable,
                 sentence_handler: SentenceHandler,
                 random_state: int = 12345
                 ):
        """

        """
        np.random.seed(random_state)
        self.model = model
        self.sentence_handler = sentence_handler
        self.random_state = random_state

