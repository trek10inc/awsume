import os
import sys

import colorama
import yaml
from colorama import init

from . constants import AWSUME_CONFIG


def safe_print(message: str, color: str = '', end: str = None):
    """Safely print so no data is interfering with the shell wrapper"""
    try:
        config = yaml.safe_load(open(str(AWSUME_CONFIG), 'r')) or {}
    except:
        config = {}
    if os.name == 'nt' or config.get('colors') != True:
        color = ''
    print(str(color) + str(message) + colorama.Style.RESET_ALL, end=end, file=sys.stderr)
