import os
import sys
import json
import configparser
from pathlib import Path


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


def main():
    config, credentials = get_aws_files()
    profile_names = get_profile_names(credentials, config)
    autocomplete_file = str(Path('~/.awsume/autocomplete.json').expanduser())
    if os.path.isfile(autocomplete_file):
        autocomplete = json.load(open(autocomplete_file))
        profile_names = uniquely_concat_lists(profile_names, autocomplete['profile-names'])
    print('\n'.join(profile_names))


if __name__ == "__main__":
    main()
