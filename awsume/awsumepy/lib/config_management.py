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
    if not options:
        options = defaults
    return options


def write_config(config: dict):
    if not os.path.exists(str(constants.AWSUME_DIR)):
        os.makedirs(str(constants.AWSUME_DIR))
    if not os.path.isfile(str(constants.AWSUME_CONFIG)):
        open(str(constants.AWSUME_CONFIG), 'a').close()

    try:
        yaml.safe_dump(config, open(str(constants.AWSUME_CONFIG), 'w'), width=1000)
    except Exception as e:
        safe_print('Unable to write config: {}'.format(e), colorama.Fore.RED)


def update_config(operations: list):
    logger.debug('Updating config: {}'.format(', '.join(operations)))
    config = load_config()

    if operations[0].lower() == 'set':
        if len(operations) < 3:
            safe_print('Must supply value to set {} to'.format(operations[1]))
            exit(1)
        logger.debug('Setting {} to {}'.format(operations[1], operations[2]))
        values = operations[2:]
        for index, value in enumerate(values):
            try:
                values[index] = json.loads(operations[2])
            except json.JSONDecodeError:
                logger.debug('Cannot parse input', exc_info=True)
        if len(values) == 1:
            value = values[0]
        else:
            value = values

        parts = operations[1].split('.') # ['console', 'command']
        location = config
        for path in parts[:-1]:
            if path in location:
                location = location[path]
            else:
                location[path] = {}
                location = location[path]
        location[parts[-1]] = value

    if operations[0].lower() in ['reset']:
        parts = operations[1].split('.')
        location = config
        default_location = defaults
        for path in parts[:-1]:
            if path in default_location:
                default_location = default_location[path]
            else:
                safe_print('Key does not have a default: {}'.format(operations[1]), colorama.Fore.YELLOW)
                exit(1)
            if path in location:
                location = location[path]
            else:
                safe_print('No such key in config: {}'.format(operations[1]), colorama.Fore.YELLOW)
                exit(1)
        if location.get(parts[-1]) is not None and default_location.get(parts[-1]) is not None:
            location[parts[-1]] = default_location[parts[-1]]
            safe_print('Reset key {} to {}'.format(operations[1], default_location[parts[-1]]), colorama.Fore.YELLOW)
        else:
            safe_print('No such key {}'.format(operations[1]))

    if operations[0].lower() in ['clear']:
        parts = operations[1].split('.')
        location = config
        for path in parts[:-1]:
            if path in location:
                location = location[path]
            else:
                break
        if location.get(parts[-1]):
            del location[parts[-1]]
            safe_print('Deleted key {}'.format(operations[1]), colorama.Fore.YELLOW)

    write_config(config)
