import os
import sys
import logging
from logging import StreamHandler, Formatter, INFO, WARN, ERROR


def set_streamhandler(logger):
    logger.setLevel(INFO)
    _handler = StreamHandler(sys.stdout)
    _handler.setFormatter(
        Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(_handler)


DISABLE_LOGGER_STREAMOUTPUT = "QM_DISABLE_STREAMOUTPUT"
logger = logging.getLogger("qm")
if os.environ.get(DISABLE_LOGGER_STREAMOUTPUT, None) is None:
    set_streamhandler(logger)

__all__ = ["INFO", "WARN", "ERROR", "logger"]
