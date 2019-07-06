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


# remove traceback on ctrl+C
def __exit_awsume(arg1, arg2): # pragma: no cover
    """Make sure ^C doesn't spam the terminal."""
    print('')
    sys.exit(1)
signal.signal(signal.SIGINT, __exit_awsume)


def run_awsume(argument_list):
    awsume = app.Awsume()
    awsume.run(argument_list)


def main():
    if '--debug' in sys.argv:
        logger.setLevel(logging.DEBUG)
        logger.debug('Debug logs are visible')
    elif '--info' in sys.argv:
        logger.setLevel(logging.INFO)
        logger.info('Info logs are visible')
    logger.debug('Executing awsume')
    run_awsume(sys.argv)
