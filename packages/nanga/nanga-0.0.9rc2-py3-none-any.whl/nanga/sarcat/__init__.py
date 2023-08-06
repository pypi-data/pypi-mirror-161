# @copyright  Copyright (c) 2018-2020 Opscidia

import logging

from .models import legacy

__version__ = '1.0.0beta'

logger = logging.getLogger('sarcat')
if not logger.handlers:  # To ensure reload() doesn't add another one
    logger.addHandler(logging.NullHandler())
