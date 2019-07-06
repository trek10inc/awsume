import sys
import json
import colorama
from colorama import init
from .constants import AWSUME_CONFIG

def safe_print(message: str, color: str = '', end: str = None):
    """Safely print so no data is interfering with the shell wrapper"""
    config = json.load(open(str(AWSUME_CONFIG), 'r'))
    if config.get('colors') != 'true':
        color = ''
    print(str(color) + str(message) + colorama.Style.RESET_ALL, end=end, file=sys.stderr)
