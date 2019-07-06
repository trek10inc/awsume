import os
import json
import colorama

from . import constants
from . logger import logger
from . safe_print import safe_print


defaults = {
    'role-duration': '0',
}


def load_config() -> dict:
    if not os.path.exists(str(constants.AWSUME_DIR)):
        os.makedirs(str(constants.AWSUME_DIR))
    if not os.path.isfile(str(constants.AWSUME_CONFIG)):
        open(str(constants.AWSUME_CONFIG), 'a').close()

    try:
        options = json.load(open(str(constants.AWSUME_CONFIG), 'r'))
    except Exception:
        write_config(defaults)
    return options


def write_config(config: dict):
    if not os.path.exists(str(constants.AWSUME_DIR)):
        os.makedirs(str(constants.AWSUME_DIR))
    if not os.path.isfile(str(constants.AWSUME_CONFIG)):
        open(str(constants.AWSUME_CONFIG), 'a').close()

    try:
        json.dump(config, open(str(constants.AWSUME_CONFIG), 'w'), indent=2)
    except Exception as e:
        safe_print(colorama.Fore.RED + 'Unable to write cache: {}'.format(e))
        pass


def update_config(operations: list):
    logger.debug('Updating config: {}'.format(', '.join(operations)))
    config = load_config()
    if operations[0].lower() == 'set':
        logger.debug('Setting {} to {}'.format(operations[1], operations[2]))
        config[operations[1]] = operations[2]
    if operations[0].lower() in ['reset', 'clear']:
        if operations[1] in defaults:
            config[operations[1]] = defaults[operations[1]]
            safe_print(colorama.Fore.YELLOW + 'Reset {} to {}'.format(operations[1], defaults[operations[1]]))
        else:
            pass
            safe_print(colorama.Fore.YELLOW + 'Key not a valid default: {}'.format(operations[1]))
    write_config(config)
