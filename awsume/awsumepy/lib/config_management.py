import json
import os
import sys
from shutil import move

import colorama

import yaml

from . import exceptions
from . import constants
from .logger import logger
from .safe_print import safe_print


defaults = {
    'role-duration': 0,
    'colors': True,
    'fuzzy-match': False,
}


CONFIG_MANAGEMENT_HELP = """
usage: --config operation [operands]
operations:
  - help
  - list
  - get [config_key]
  - set [config_key] [config_value]
"""

def migrate_to_xdg_base_directories() -> None:
    if not os.path.exists(str(constants.AWSUME_DIR)):
        os.makedirs(str(constants.AWSUME_DIR))
    if not os.path.exists(str(constants.AWSUME_CONFIG.parent)):
        os.makedirs(str(constants.AWSUME_CONFIG.parent))
    if not os.path.isfile(str(constants.AWSUME_CONFIG)):
        open(str(constants.AWSUME_CONFIG), 'a').close()
    if not os.path.exists(str(constants.AWSUME_LOG_DIR)):
        os.makedirs(str(constants.AWSUME_LOG_DIR))
    if constants.IS_USING_XDG_CONFIG_HOME and os.path.isfile(constants.AWSUME_CONFIG_LEGACY_PATH):
        # handle migration to XDG base directory: config file
        move(constants.AWSUME_CONFIG_LEGACY_PATH, constants.AWSUME_CONFIG)
    if constants.IS_USING_XDG_CACHE_HOME and os.path.isdir(constants.AWSUME_CACHE_DIR_LEGACY_PATH):
        # handle migration to XDG base directory: cache dir
        move(constants.AWSUME_CACHE_DIR_LEGACY_PATH, constants.AWSUME_CACHE_DIR)
    if constants.IS_USING_XDG_DATA_HOME and os.path.isdir(constants.AWSUME_CACHE_DIR_LEGACY_PATH):
        # handle migration to XDG base directory: data dir
        move(constants.AWSUME_DIR_LEGACY_PATH, constants.AWSUME_DIR)
    if constants.IS_USING_XDG_STATE_HOME and os.path.isdir(constants.AWSUME_LOG_DIR_LEGACY_PATH):
        # handle migration to XDG base directory: log dir
        move(constants.AWSUME_LOG_DIR_LEGACY_PATH, constants.AWSUME_LOG_DIR)
    if (
            constants.IS_USING_XDG_CONFIG_HOME and
            constants.IS_USING_XDG_DATA_HOME and
            constants.IS_USING_XDG_CACHE_HOME and
            constants.IS_USING_XDG_STATE_HOME and
            os.path.isdir(constants.AWSUME_DIR_LEGACY_PATH)
    ):
        # cleanup legacy ~/.awsume dir
        os.rmdir(constants.AWSUME_DIR_LEGACY_PATH)

def load_config() -> dict:
    migrate_to_xdg_base_directories()

    options = None
    try:
        options = yaml.safe_load(open(str(constants.AWSUME_CONFIG), 'r'))
    except Exception as e:
        raise exceptions.ConfigParseException(constants.AWSUME_CONFIG, message='Cannot parse config file', error=e)
    if options is None:
        options = defaults
        write_config(options)
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


def handle_config(operations: list):
    logger.debug('Updating config: {}'.format(', '.join(operations)))
    config = load_config()

    if not len(operations):
        raise exceptions.ConfigOperationException('Must supply a config management operand')

    if operations[0].lower() == 'help':
        safe_print(CONFIG_MANAGEMENT_HELP)
        raise exceptions.EarlyExit()

    if operations[0].lower() == 'get':
        if len(operations) != 2:
            raise exceptions.ConfigOperationException('Must supply value to get')
        logger.debug('Getting {}'.format(operations[1]))
        value = get_dict_parts(config, operations[1])
        safe_print(json.dumps(value))
        raise exceptions.EarlyExit()

    if operations[0].lower() == 'list':
        if len(operations) != 1:
            raise exceptions.ConfigOperationException('No operands are valid for operation "list"')
        logger.debug('Listing config')
        yaml.safe_dump(config, sys.stderr, width=1000)
        raise exceptions.EarlyExit()

    if operations[0].lower() == 'set':
        if len(operations) < 3:
            raise exceptions.ConfigOperationException('Must supply value to set {} to'.format(operations[1]))
        logger.debug('Setting {} to {}'.format(operations[1], operations[2]))
        value = get_value_from_args(operations[2:])
        config = update_dict_parts(config, operations[1], value)

    if operations[0].lower() in ['reset']:
        default_value = get_dict_parts(defaults, operations[1])
        if default_value is None:
            raise exceptions.ConfigOperationException('Key does not have a default: {}'.format(operations[1]), colorama.Fore.YELLOW)
        config = update_dict_parts(config, operations[1], default_value)
        safe_print('Reset key {} to {}'.format(operations[1], default_value), colorama.Fore.YELLOW)

    if operations[0].lower() in ['clear']:
        config, deleted = delete_dict_value_parts(config, operations[1])
        if deleted:
            safe_print('Deleted key {}'.format(operations[1]), colorama.Fore.YELLOW)

    write_config(config)


def get_value_from_args(args):
    values = args
    for index, value in enumerate(args):
        try:
            values[index] = json.loads(value)
        except json.JSONDecodeError:
            logger.debug('Cannot parse input', exc_info=True)
    return values[0] if len(values) == 1 else values


def get_dict_parts(obj, parts_string):
    parts = parts_string.split('.')
    location = obj
    for path in parts:
        if path in location:
            location = location[path]
        else:
            return None
    return location


def update_dict_parts(obj, parts_string, value):
    parts = parts_string.split('.')
    location = obj
    for path in parts[:-1]:
        if path in location:
            location = location[path]
        else:
            location[path] = {}
            location = location[path]
    location[parts[-1]] = value
    return obj


def delete_dict_value_parts(obj, parts_string):
    parts = parts_string.split('.')
    location = obj
    for path in parts[:-1]:
        if path in location:
            location = location[path]
        else:
            return obj, False
    del location[parts[-1]]
    return obj, True
