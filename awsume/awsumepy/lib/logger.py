import sys
import logging
import re


class LogFormatter(logging.Formatter):
    @staticmethod
    def _filter(s):
        no_access_key_id = re.sub(r'(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])', 'SECRET', s)
        no_secret_access_key = re.sub(r'(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])', 'SECRET', no_access_key_id)
        return no_secret_access_key

    def format(self, record):
        original = logging.Formatter.format(self, record)
        return self._filter(original)


logger = logging.getLogger('awsume') # type: logging.Logger
LOG_HANDLER = logging.StreamHandler()
LOG_HANDLER.setFormatter(LogFormatter('[%(asctime)s] %(filename)s:%(funcName)s : [%(levelname)s] %(message)s'))
logger.addHandler(LOG_HANDLER)
