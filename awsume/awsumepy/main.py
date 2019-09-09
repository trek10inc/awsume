import sys
import argparse
import pluggy
import signal
import logging

from .. import __data__
from . import hookspec
from . import default_plugins
from . import app
from . lib.logger import logger
from . lib.safe_print import safe_print


def run_awsume(argument_list):
    awsume = app.Awsume()
    awsume.run(argument_list)


def main():
    try:
        if '--debug' in sys.argv:
            logger.setLevel(logging.DEBUG)
            logger.debug('Debug logs are visible')
        elif '--info' in sys.argv:
            logger.setLevel(logging.INFO)
            logger.info('Info logs are visible')
        logger.debug('Executing awsume')
        run_awsume(sys.argv[1:])
    except KeyboardInterrupt:
        pass
