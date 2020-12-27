import argparse
import json
import re
import operator
from datetime import datetime
import dateutil
import colorama
import difflib
from . import exceptions
from . logger import logger
from . safe_print import safe_print
from . import aws as aws_lib
from collections import OrderedDict
from difflib import SequenceMatcher

VALID_CREDENTIAL_SOURCES = [ None, 'Environment', 'Ec2InstanceMetadata', 'EcsContainer' ]
try:
    import Levenshtein
except:
    Levenshtein = False


def parse_time(date_time: datetime):
    date_time.replace(tzinfo=dateutil.tz.tzlocal())
    return date_time.strftime('%Y-%m-%d %H:%M:%S')


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


def validate_profile(config: dict, arguments: argparse.Namespace, profiles: dict, target_profile_name: str) -> bool:
    logger.debug('Validating profile')
    profile = profiles.get(target_profile_name)
    if arguments.output_profile and not is_mutable_profile(profiles, arguments.output_profile):
        raise exceptions.ImmutableProfileError(arguments.output_profile, 'not awsume-managed')
    if not profile:
        raise exceptions.ProfileNotFoundError(profile_name=target_profile_name)

    # validate role profiles
    if 'role_arn' in profile:
        if profile.get('credential_source') and profile.get('source_profile'):
            raise exceptions.InvalidProfileError(target_profile_name, message='credential_source and source_profile are mutually exclusive profile options')
        if not profile.get('credential_source') and not profile.get('credential_process') and not profile.get('source_profile') and not profile.get('principal_arn'):
            raise exceptions.InvalidProfileError(target_profile_name, message='role profiles must contain one of credential_source or source_profile or credential_process')
        if profile.get('credential_source') not in VALID_CREDENTIAL_SOURCES:
            raise exceptions.InvalidProfileError(target_profile_name, message='unsupported awsume credential_source profile option: {}'.format(profile.get('credential_source')))
        source_profile_name = profile.get('source_profile')
        source_profile = get_source_profile(profiles, target_profile_name)
        if source_profile_name and not source_profile:
            raise exceptions.ProfileNotFoundError(profile_name=source_profile_name)
        if source_profile and not source_profile.get('role_arn'):
            user_profile = source_profile
            user_profile_name = source_profile_name
        else:
            user_profile = None
            user_profile_name = None
    else:
        user_profile = profile
        user_profile_name = target_profile_name

    # validate user profile
    if user_profile:
        missing_keys = []
        if 'credential_source' in profile:
            if profile.get('credential_source') not in VALID_CREDENTIAL_SOURCES:
                raise exceptions.InvalidProfileError(user_profile_name, message='unsupported awsume credential_source profile option: {}'.format(profile.get('credential_source')))
        elif not 'credential_process' in user_profile and not 'credential_process' in profile:
            if 'aws_access_key_id' not in user_profile:
                missing_keys.append('aws_access_key_id')
            if 'aws_secret_access_key' not in user_profile:
                missing_keys.append('aws_secret_access_key')
        if missing_keys:
            raise exceptions.InvalidProfileError(user_profile_name, message='Missing keys {}, or credential_source, or credential_process'.format(', '.join(missing_keys)))

    return True


def is_mutable_profile(profiles: dict, profile_name: str) -> dict:
    profile = profiles.get(profile_name)
    if not profile:
        return True
    if profile.get('manager') == 'awsume':
        return True
    return False


def get_source_profile(profiles: dict, target_profile_name: str) -> dict:
    target_profile = profiles.get(target_profile_name)
    if target_profile:
        source_profile_name = target_profile.get('source_profile', 'default')
        return profiles.get(source_profile_name)
    return None


def get_role_chain(config: dict, arguments: argparse.Namespace, profiles: dict, target_profile_name: str) -> list:
    logger.debug('Getting role chain for [{}]'.format(target_profile_name))
    target_profile = profiles.get(target_profile_name)

    if not target_profile or not target_profile.get('role_arn') or get_role_duration(config, arguments, target_profile):
        return [target_profile_name]

    role_chain = []
    while target_profile:
        logger.debug('target profile: {}'.format(json.dumps(target_profile, default=str)))
        if target_profile_name in role_chain:
            raise exceptions.InvalidProfileError(','.join(role_chain), 'cannot have circular role-chains')
        role_chain.append(target_profile_name)
        target_profile_name = target_profile.get('source_profile')
        # if mfa required on role arn, get longer 12-hour session credentials first by doing mfa on the source profile
        if 'role_arn' in target_profile and 'mfa_serial' in target_profile:
            profiles[target_profile_name]['mfa_serial'] = target_profile['mfa_serial']
        target_profile = profiles.get(target_profile_name)
    role_chain.reverse()
    return role_chain


def get_region(profiles: dict, arguments: argparse.Namespace, config: dict, ignore_config: bool = False, ignore_default: bool = False) -> str:
    if arguments.region:
        return arguments.region
    if arguments.role_arn and arguments.source_profile and profiles.get(arguments.source_profile, {}).get('region'):
        return profiles[arguments.source_profile]['region']
    target_profile = profiles.get(arguments.target_profile_name, {})
    if target_profile.get('region'):
        return target_profile['region']
    source_profile = get_source_profile(profiles, arguments.target_profile_name)
    if source_profile and source_profile.get('region'):
        return source_profile['region']
    if not ignore_default and profiles.get('default', {}).get('region'):
        return profiles['default']['region']
    if not ignore_config and config.get('region'):
        return config['region']
    return None


def get_session_name(config: dict, arguments: argparse.Namespace, profiles: dict, target_profile_name: str) -> dict:
    target_profile = profiles.get(target_profile_name)
    if arguments.session_name:
        return arguments.session_name
    if target_profile and target_profile.get('role_session_name'):
        return target_profile['role_session_name']
    if config.get('role-session-name'):
        return config['role-session-name']
    if target_profile_name:
        return target_profile_name
    return 'awsume-session'


def get_external_id(arguments: argparse.Namespace, target_profile: dict):
    if arguments.external_id:
        return arguments.external_id
    return target_profile.get('external_id')


def get_role_duration(config: dict, arguments: argparse.Namespace, target_profile: dict):
    if arguments.role_duration:
        return int(arguments.role_duration)
    if target_profile.get('duration_seconds'):
        return int(target_profile.get('duration_seconds'))
    if config.get('role-duration'):
        return int(config.get('role-duration'))
    return 0


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
            is_role_profile = 'role_arn' in profile
            profile_type = 'Role' if is_role_profile else 'User'
            # Assume source_profile is None unless we find otherwise afterwards.
            if is_role_profile:
                if 'source_profile' in profile.keys():
                    source_profile = profile['source_profile']
                elif 'principal_arn' in profile.keys():
                    source_profile = profile['principal_arn'].split(':')[-1]
                else:
                    source_profile = 'None'
            else:
                source_profile = 'None'
            mfa_needed = 'Yes' if 'mfa_serial' in profile else 'No'
            profile_region = str(profile.get('region')) or str(profile.get('sso_region'))
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


def list_profile_data(profiles: dict, get_extra_data: bool, config: dict): # pragma: no cover
    profiles = {k: v for k, v in profiles.items() if not v.get('autoawsume')}
    if config.get('is_interactive'):
        formatted_profiles = format_aws_profiles(profiles, get_extra_data)
        print_formatted_data(formatted_profiles)
    return profiles


def get_account_id(profile: dict, call_aws: bool = False) -> str:
    logger.info('Getting account ID from profile: %s', json.dumps(profile, indent=2))
    if profile.get('sso_account_id'):
        return profile['sso_account_id']
    if profile.get('role_arn'):
        return profile['role_arn'].replace('arn:aws:iam::', '').split(':')[0]
    if profile.get('mfa_serial'):
        return profile['mfa_serial'].replace('arn:aws:iam::', '').split(':')[0]
    if call_aws and profile.get('aws_access_key_id') and profile.get('aws_secret_access_key'):
        return aws_lib.get_account_id(profile_to_credentials(profile))
    return 'Unavailable'


def get_profile_name(config: dict, profiles: dict, target_profile_name: str, log=True) -> str:
    if target_profile_name in profiles or not config.get('fuzzy-match'):
        return target_profile_name
    profile_names = list(profiles.keys())

    matched_prefix_profile = match_prefix(profile_names, target_profile_name)
    if matched_prefix_profile:
        if log:
            safe_print('Using profile ' + matched_prefix_profile, color=colorama.Fore.YELLOW)
        return matched_prefix_profile

    matched_contains_profile = match_contains(profile_names, target_profile_name)
    if matched_contains_profile:
        if log:
            safe_print('Using profile ' + matched_contains_profile, color=colorama.Fore.YELLOW)
        return matched_contains_profile

    matched_levenshtein_profile = match_levenshtein(profile_names, target_profile_name)
    if matched_levenshtein_profile:
        if log:
            safe_print('Using profile ' + matched_levenshtein_profile, color=colorama.Fore.YELLOW)
        return matched_levenshtein_profile

    return target_profile_name


def match_prefix(profile_names: list, profile_name: str) -> str:
    prefix_words = [_ for _ in profile_names if _.startswith(profile_name)]
    if len(prefix_words) == 1:
        return prefix_words[0]
    return None


def match_contains(profile_names: list, profile_name: str) -> str:
    def longest_contains(str1, str2):
        sequence_match = SequenceMatcher(None,str1,str2)
        match = sequence_match.find_longest_match(0, len(str1), 0, len(str2))
        return match.size

    matches = {profile: longest_contains(profile_name, profile) for profile in profile_names}
    biggest_match = max(matches.values())
    result = [k for k in matches.keys() if matches[k] == biggest_match]
    if len(result) == 1:
        return result[0]
    return None


def match_levenshtein(profile_names: list, profile_name: str) -> str:
    if not Levenshtein:
        logger.debug('Levenshtein not installed, try installing awsume[fuzzy]')
        return None
    matches = {profile: Levenshtein.distance(profile_name, profile) for profile in profile_names}
    closest_match = min(matches.values())
    result = [k for k in matches.keys() if matches[k] == closest_match]
    if len(result) == 1:
        return result[0]
    return None
