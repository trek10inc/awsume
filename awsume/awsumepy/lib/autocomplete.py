import os
import configparser
import json
from pathlib import Path
import boto3

REGIONS = [
    'us-east-2',
    'us-east-1',
    'us-west-1',
    'us-west-2',
    'ap-east-1',
    'ap-south-1',
    'ap-northeast-3',
    'ap-northeast-2',
    'ap-southeast-1',
    'ap-southeast-2',
    'ap-northeast-1',
    'ca-central-1',
    'cn-north-1',
    'cn-northwest-1',
    'eu-central-1',
    'eu-west-1',
    'eu-west-2',
    'eu-west-3',
    'eu-north-1',
    'me-south-1',
    'sa-east-1',
    'us-gov-east-1',
    'us-gov-west-1',
]


def get_aws_files() -> tuple:
    config_file = os.environ.get('AWS_CONFIG_FILE') if os.environ.get('AWS_CONFIG_FILE') else '~/.aws/config'
    credentials_file = os.environ.get('AWS_CREDENTIALS_FILE') if os.environ.get('AWS_CREDENTIALS_FILE') else '~/.aws/credentials'
    return str(Path(config_file).expanduser()), str(Path(credentials_file).expanduser())


def get_profile_names(credentials_file: str, config_file: str) -> list:
    credentials = configparser.ConfigParser()
    credentials.read(credentials_file)
    profiles = list(credentials._sections.keys())

    config = configparser.ConfigParser()
    config.read(config_file)
    config_profiles = [_.replace('profile ', '') for _ in list(config._sections.keys())]

    return uniquely_concat_lists(profiles, config_profiles)


def uniquely_concat_lists(list1, list2):
    for element in list2:
        if element not in list1:
            list1.append(element)
    return list1


def profile_name_completer(prefix, parsed_args, **kwargs):
    config, credentials = get_aws_files()
    profile_names = get_profile_names(credentials, config)
    autocomplete_file = str(Path('~/.awsume/autocomplete.json').expanduser())
    if os.path.isfile(autocomplete_file):
        autocomplete = json.load(open(autocomplete_file))
        profile_names = uniquely_concat_lists(profile_names, autocomplete['profile-names'])
    return [profile_name for profile_name in profile_names if profile_name.startswith(prefix)]


def region_completer(prefix, parsed_args, **kwargs):
    return [region for region in REGIONS if region.startswith(prefix)]
