import os
import argparse
import configparser
import colorama
from datetime import datetime
from pathlib import Path

from . import constants
from . safe_print import safe_print


def get_aws_files(args: argparse.Namespace, config: dict) -> tuple:
    if os.environ.get('AWS_CONFIG_FILE'):
        config_file = os.environ.get('AWS_CONFIG_FILE')
    elif args and args.config_file:
        config_file = args.config_file
    elif config and config.get('config-file'):
        config_file = config.get('config-file')
    else:
        config_file = constants.DEFAULT_CONFIG_FILE

    if os.environ.get('AWS_SHARED_CREDENTIALS_FILE'):
        credentials_file = os.environ.get('AWS_SHARED_CREDENTIALS_FILE')
    elif args and  args.credentials_file:
        credentials_file = args.credentials_file
    elif config and config.get('credentials-file'):
        credentials_file = config.get('credentials-file')
    else:
        credentials_file = constants.DEFAULT_CREDENTIALS_FILE

    return str(Path(config_file)), str(Path(credentials_file))


def add_section(name: str, section: dict, file_name: str, overwrite: bool = False):
    config = configparser.ConfigParser()
    config.read(file_name)
    if config.has_section(name):
        if not overwrite:
            safe_print('Cannot overwrite data in {}'.format(file_name), colorama.Fore.RED)
            return
        config.remove_section(name)
    config.add_section(name)
    config.set(name, 'manager', 'awsume')
    for key in section:
        config.set(name, key, str(section[key]))
    config.write(open(str(file_name), 'w'))


def get_section(name: str, file_name: str):
    config = configparser.ConfigParser()
    config.read(file_name)
    return config._sections.get(name, {})


def delete_section(name: str, file_name: str):
    config = configparser.ConfigParser()
    config.read(file_name)
    if config.has_section(name):
        config.remove_section(name)
    config.write(open(str(file_name), 'w'))


def read_aws_file(file_name: str) -> dict:
    config = configparser.ConfigParser()
    config.read(file_name)
    profiles = {k: dict(v) for k, v in config._sections.items()}
    return profiles


def remove_expired_output_profiles(file_name: str) -> dict:
    config = configparser.ConfigParser()
    config.read(file_name)
    for section in config.sections():
        if config.has_option(section, 'manager') and config.get(section, 'manager') != 'awsume':
            continue
        if config.has_option(section, 'autoawsume'):
            continue
        if config.has_option(section, 'expiration'):
            expiration = datetime.strptime(config.get(section, 'expiration'), '%Y-%m-%d %H:%M:%S')
            if expiration < datetime.now():
                config.remove_section(section)
    config.write(open(str(file_name), 'w'))
