import os
import json
import colorama

from . import constants
from . logger import logger
from . safe_print import safe_print


defaults = {
    'role-duration': '0',
    'colors': 'true'
}


def load_config() -> dict:
    if not os.path.exists(str(constants.AWSUME_DIR)):
        os.makedirs(str(constants.AWSUME_DIR))
    if not os.path.isfile(str(constants.AWSUME_CONFIG)):
        open(str(constants.AWSUME_CONFIG), 'a').close()

    options = {}
    try:
        options = json.load(open(str(constants.AWSUME_CONFIG), 'r'))
    except json.JSONDecodeError:
        write_config(defaults)
        options = defaults
    return options


def write_config(config: dict):
    if not os.path.exists(str(constants.AWSUME_DIR)):
        os.makedirs(str(constants.AWSUME_DIR))
    if not os.path.isfile(str(constants.AWSUME_CONFIG)):
        open(str(constants.AWSUME_CONFIG), 'a').close()

    try:
        json.dump(config, open(str(constants.AWSUME_CONFIG), 'w'), indent=2)
    except Exception as e:
        safe_print('Unable to write config: {}'.format(e), colorama.Fore.RED)


def update_config(operations: list):
    logger.debug('Updating config: {}'.format(', '.join(operations)))
    config = load_config()
    if operations[0].lower() == 'set':
        logger.debug('Setting {} to {}'.format(operations[1], operations[2]))
        config[operations[1]] = operations[2]
    if operations[0].lower() in ['reset', 'clear']:
        if operations[1] in defaults:
            config[operations[1]] = defaults[operations[1]]
            safe_print('Reset {} to {}'.format(operations[1], defaults[operations[1]]), colorama.Fore.YELLOW)
        else:
            safe_print('Key not a valid default: {}'.format(operations[1]), colorama.Fore.YELLOW)
    write_config(config)
