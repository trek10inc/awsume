import sys
import json
from colorama import init
from .constants import AWSUME_CONFIG

def safe_print(*args, **kwargs):
    """Safely print so no data is interfering with the shell wrapper"""
    if not kwargs.get('file'):
        kwargs['file'] = sys.stderr
    # config = json.load(open(str(AWSUME_CONFIG), 'r'))
    # if config.get('colors'):
    #     print('Colors enabled', **kwargs)
    print(*args, **kwargs)
