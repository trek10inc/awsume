import sys
import logging

logger = logging.getLogger('awsume') # type: logging.Logger
LOG_HANDLER = logging.StreamHandler()
LOG_HANDLER.setFormatter(logging.Formatter('[%(asctime)s] %(filename)s:%(funcName)s : [%(levelname)s] %(message)s'))
logger.addHandler(LOG_HANDLER)


