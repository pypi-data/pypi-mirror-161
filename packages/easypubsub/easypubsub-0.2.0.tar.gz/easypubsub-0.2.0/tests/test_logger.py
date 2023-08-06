import logging

from easypubsub.logging import getLogger

_logger = getLogger(__name__, log_level=logging.DEBUG)
_logger.info("This is a test message.")
_logger.debug("This is a debug test message.")
