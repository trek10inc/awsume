import argparse
import json
import re
import colorama
from . exceptions import ProfileNotFoundError, InvalidProfileError
from . logger import logger
from . safe_print import safe_print
from . import aws as aws_lib
from collections import OrderedDict

VALID_CREDENTIAL_SOURCES = [ None, 'Environment' ]


def is_role(profile: dict) -> bool:
    return 'role_arn' in profile


def profile_to_credentials(profile: dict) -> dict:
    if profile:
        return {
            'AccessKeyId': profile.get('aws_access_key_id'),
            'SecretAccessKey': profile.get('aws_secret_access_key'),
            'SessionToken': profile.get('aws_session_token'),
            'Region': profile.get('region'),
        }
    return {}

def credentials_to_profile(credentials: dict) -> dict:
    result =  {}
    if credentials.get('AccessKeyId'):
        result['aws_access_key_id'] = credentials['AccessKeyId']
    if credentials.get('SecretAccessKey'):
        result['aws_secret_access_key'] = credentials['SecretAccessKey']
    if credentials.get('SessionToken'):
        result['aws_session_token'] = credentials['SessionToken']
    if credentials.get('Region'):
        result['region'] = credentials['Region']
    return result


def validate_profile(profiles: dict, target_profile_name: str) -> bool:
    logger.debug('Validating profile')
    profile = profiles.get(target_profile_name)
    if not profile:
        raise ProfileNotFoundError(profile_name=target_profile_name)

    # validate role profiles
    if is_role(profile):
        if profile.get('credential_process'):
            raise InvalidProfileError(target_profile_name, message='awsume does not support the credential_process profile option: {}')
        if profile.get('credential_source') and profile.get('source_profile'):
            raise InvalidProfileError(target_profile_name, message='credential_source and source_profile are mutually exclusive profile options')
        if not profile.get('credential_source') and not profile.get('source_profile'):
            raise InvalidProfileError(target_profile_name, message='role profiles must contain one of credential_source or source_profile')
        if profile.get('credential_source') not in VALID_CREDENTIAL_SOURCES:
            raise InvalidProfileError(target_profile_name, message='unsupported awsume credential_source profile option: {}'.format(profile.get('credential_source')))
        source_profile_name = profile.get('source_profile')
        if source_profile_name and not profiles.get(source_profile_name):
            raise ProfileNotFoundError(profile_name=source_profile_name)
        user_profile = get_source_profile(profiles, target_profile_name)
        user_profile_name = source_profile_name
    else:
        user_profile = profile
        user_profile_name = target_profile_name

    # validate user profile
    if user_profile:
        missing_keys = []
        if 'aws_access_key_id' not in user_profile:
            missing_keys.append('aws_access_key_id')
        if 'aws_secret_access_key' not in user_profile:
            missing_keys.append('aws_secret_access_key')
        if missing_keys:
            raise InvalidProfileError(user_profile_name, message='Missing keys {}'.format(', '.join(missing_keys)))
    return True


def get_source_profile(profiles: dict, target_profile_name: str) -> dict:
    target_profile = profiles.get(target_profile_name)
    if target_profile:
        source_profile_name = target_profile.get('source_profile', 'default')
        return profiles.get(source_profile_name)
    return None


def get_region(profiles: dict, arguments: argparse.Namespace) -> str:
    if arguments.region:
        return arguments.region
    if arguments.role_arn and arguments.source_profile:
        return profiles.get(arguments.source_profile, {}).get('region')
    target_profile = profiles.get(arguments.target_profile_name, {})
    if target_profile.get('region'):
        return target_profile['region']
    source_profile = get_source_profile(profiles, arguments.target_profile_name)
    if source_profile and source_profile.get('region'):
        return source_profile['region']
    return None


def get_mfa_serial(profiles: dict, target_profile_name: str) -> dict:
    target_profile = profiles.get(target_profile_name)
    mfa_serial = target_profile.get('mfa_serial')
    if not mfa_serial:
        source_profile_name = target_profile.get('source_profile')
        mfa_serial = profiles.get(source_profile_name, {}).get('mfa_serial')
    return mfa_serial


def get_mfa_token() -> str:
    token_pattern = re.compile('^[0-9]{6}$')
    safe_print('Enter MFA token: ', colorama.Fore.CYAN, end='')
    while True:
        mfa_token = input()
        if token_pattern.match(mfa_token):
            return mfa_token
        else:
            safe_print('Please enter a valid MFA token: ', colorama.Fore.CYAN, end='')


def aggregate_profiles(result: list) -> dict:
    return_profiles = {}
    for profiles in result:
        for profile_name, profile in profiles.items():
            if profile_name not in return_profiles:
                return_profiles[profile_name] = profile
            else:
                return_profiles[profile_name].update(profile)
    return return_profiles


def format_aws_profiles(profiles: dict, get_extra_data: bool) -> list: # pragma: no cover
    sorted_profiles = OrderedDict(sorted(profiles.items()))
    # List headers
    list_headers = ['PROFILE', 'TYPE', 'SOURCE', 'MFA?', 'REGION', 'ACCOUNT']
    profile_list = []
    profile_list.append([])
    profile_list[0].extend(list_headers)
    # now fill the tables with the appropriate data
    for name in sorted_profiles:
        #don't add any autoawsume profiles
        if 'auto-refresh-' not in name:
            profile = sorted_profiles[name]
            is_role_profile = is_role(profile)
            profile_type = 'Role' if is_role_profile else 'User'
            source_profile = profile['source_profile'] if is_role_profile else 'None'
            mfa_needed = 'Yes' if 'mfa_serial' in profile else 'No'
            profile_region = str(profile.get('region'))
            profile_account_id = get_account_id(profile, get_extra_data)
            list_row = [name, profile_type, source_profile, mfa_needed, profile_region, profile_account_id]
            profile_list.append(list_row)
    return profile_list


def print_formatted_data(profile_data: list): # pragma: no cover
    print('Listing...\n')
    widths = [max(map(len, col)) for col in zip(*profile_data)]
    print('AWS Profiles'.center(sum(widths) + 10, '='))
    for row in profile_data:
        print('  '.join((val.ljust(width) for val, width in zip(row, widths))))


def list_profile_data(profiles: dict, get_extra_data: bool): # pragma: no cover
    profiles = {k: v for k, v in profiles.items() if 'autoawsume-' not in k}
    formatted_profiles = format_aws_profiles(profiles, get_extra_data)
    print_formatted_data(formatted_profiles)


def get_account_id(profile: dict, call_aws: bool = False) -> str:
    logger.info('Getting account ID from profile: %s', json.dumps(profile, indent=2))
    if profile.get('role_arn'):
        return profile['role_arn'].replace('arn:aws:iam::', '').split(':')[0]
    if profile.get('mfa_serial'):
        return profile['mfa_serial'].replace('arn:aws:iam::', '').split(':')[0]
    if call_aws and profile.get('aws_access_key_id') and profile.get('aws_secret_access_key'):
        return aws_lib.get_account_id(profile_to_credentials(profile))
    return 'Unavailable'
