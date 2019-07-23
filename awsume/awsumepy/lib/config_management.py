import json
import os

import colorama

import yaml

from . import constants
from .logger import logger
from .safe_print import safe_print


defaults = {
    'role-duration': '0',
    'colors': 'true'
}


def load_config() -> dict:
    if not os.path.exists(str(constants.AWSUME_DIR)):
        os.makedirs(str(constants.AWSUME_DIR))
    if not os.path.isfile(str(constants.AWSUME_CONFIG)):
        open(str(constants.AWSUME_CONFIG), 'a').close()

    options = None
    try:
        options = yaml.safe_load(open(str(constants.AWSUME_CONFIG), 'r'))
    except Exception:
        safe_print('Cannot parse config file: {}'.format(constants.AWSUME_CONFIG), colorama.Fore.RED)
        exit(1)
        # write_config(defaults)
        # options = defaults
    if not options:
        options = defaults
    return options


def write_config(config: dict):
    if not os.path.exists(str(constants.AWSUME_DIR)):
        os.makedirs(str(constants.AWSUME_DIR))
    if not os.path.isfile(str(constants.AWSUME_CONFIG)):
        open(str(constants.AWSUME_CONFIG), 'a').close()

    try:
        yaml.safe_dump(config, open(str(constants.AWSUME_CONFIG), 'w'))
    except Exception as e:
        safe_print('Unable to write config: {}'.format(e), colorama.Fore.RED)


def update_config(operations: list):
    logger.debug('Updating config: {}'.format(', '.join(operations)))
    config = load_config()
    if operations[0].lower() == 'set':
        logger.debug('Setting {} to {}'.format(operations[1], operations[2]))
        try:
            value = json.loads(operations[2])
        except json.JSONDecodeError:
            logger.debug('Cannot parse input', exc_info=True)
            value = operations[2]
        config[operations[1]] = value
    if operations[0].lower() in ['reset', 'clear']:
        if operations[1] in defaults:
            config[operations[1]] = defaults[operations[1]]
            safe_print('Reset {} to {}'.format(operations[1], defaults[operations[1]]), colorama.Fore.YELLOW)
        elif operations[1] in config:
            del config[operations[1]]
            safe_print('Deleted key {}'.format(operations[1]), colorama.Fore.YELLOW)
        else:
            safe_print('Key not a valid default: {}'.format(operations[1]), colorama.Fore.YELLOW)
    write_config(config)
