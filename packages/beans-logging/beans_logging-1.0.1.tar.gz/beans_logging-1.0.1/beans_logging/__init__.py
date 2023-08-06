# -*- coding: utf-8 -*-

try:
    from beans_logging.logging import logger, __version__
except ImportError:
    from .logging import logger, __version__
