"""Awsume - A cli that makes using AWS IAM credentials easy"""
from __future__ import print_function
import sys
import os
import argparse
import re
import collections
import logging
import json
import signal
import shutil
from datetime import datetime
from builtins import input as read_input
import boto3
import botocore
import psutil
import dateutil
import pkg_resources
import six
from six.moves import configparser as ConfigParser
from yapsy import PluginManager

try: # pragma: no cover
    __version__ = pkg_resources.get_distribution('awsume').version
except Exception: # pragma: no cover
    pass

# remove traceback on ctrl+C
def __exit_awsume(arg1, arg2): # pragma: no cover
    """Make sure ^C doesn't spam the terminal.
    Ignore `arg1` and `arg2`."""
    print('')
    sys.exit(0)
signal.signal(signal.SIGINT, __exit_awsume)

#initialize logging
logging.getLogger('yapsy').addHandler(logging.StreamHandler())
LOG = logging.getLogger(__name__)
LOG_HANDLER = logging.StreamHandler()
LOG_HANDLER.setFormatter(logging.Formatter('%(name)s.%(funcName)s : %(message)s'))
LOG.addHandler(LOG_HANDLER)
def __log_dt_converter(dt_object): # pragma: no cover
    """Used to convert datetime objects to strings automatically for the logger."""
    return dt_object.__str__() if isinstance(dt_object, datetime) else dt_object

#get cross-platform directories
HOME_PATH = os.path.expanduser('~')
AWS_DIRECTORY = os.path.join(HOME_PATH, '.aws')
AWS_CONFIG_FILE = os.path.join(AWS_DIRECTORY, 'config')
AWS_CREDENTIALS_FILE = os.path.join(AWS_DIRECTORY, 'credentials')
AWS_CACHE_DIRECTORY = os.path.join(AWS_DIRECTORY, 'cli/cache/')
AWSUME_PLUGIN_DIRECTORY = os.path.join(AWS_DIRECTORY, 'awsumePlugins/')
AWSUME_PLUGIN_CACHE_FILE = os.path.join(AWSUME_PLUGIN_DIRECTORY, '_plugins.json')
# AWSUME_PLUGIN_DIRECTORY = './examplePlugin/'



#
#   Exceptions
#
class ProfileNotFoundError(Exception):
    """Error that should be raised when no profile is found.
    It should only be raised after all `get_aws_profiles` functions have been called."""
class InvalidProfileError(Exception):
    """Error that should be raised when the targeted profile is invalid in some way."""
class UserAuthenticationError(Exception):
    """Error that should be raised when AWSume failed to authenticate user."""
class RoleAuthenticationError(Exception):
    """Error that should be raised when AWSume failed to authenticate the role."""



#
#   CommandLineArgumentHandling
#
def generate_argument_parser():
    """Create the argparse argument parser.

    Returns
    -------
    An `argparse` ArgumentParser
    """
    epilog = """
Usage Examples:
    Awsume the profile 'client-dev'
    $ awsume client-dev

    Awsume the profile 'client-dev', but force-refresh credentials
    $ awsume client-dev -r

    Start an auto-refresher for the 'client-dev' profile
    $ awsume client-dev -a

    Stop auto-refreshing the 'client-dev' profile
    $ awsume client-dev -k

    Awsume the profile 'client-dev' with custom RoleSessionName
    $ awsume client-dev --session-name dev-testing

    Get a list of useful profile information
    $ awsume -l

    Install a plugin
    $ awsume --install-plugin https://url/file.py https://url/file.yapsy-plugin

    Delete a plugin
    $ awsume --delete-plugin my-cool-plugin

Thank you for using AWSume! Check us out at https://trek10.com
"""
    return argparse.ArgumentParser(description=__doc__,
                                   epilog=epilog,
                                   formatter_class=lambda prog: (argparse.RawDescriptionHelpFormatter(prog, max_help_position=50)))

def add_arguments(argument_parser):
    """Add all of awsume's arguments to the argument parser.

    Parameters
    ----------
    - argument_parser - the main argument parser for awsume

    Returns
    -------
    The argument parser with the arguments added to it.
    """
    argument_parser.add_argument('-v', '--version',
                                 action='store_true',
                                 default=False,
                                 dest='version',
                                 help='Display the current version of AWSume')
    argument_parser.add_argument(action='store',
                                 dest='profile_name',
                                 nargs='?',
                                 metavar='profile_name',
                                 help='The target profile name')
    argument_parser.add_argument('-s',
                                 action='store_true',
                                 dest='show_commands',
                                 default=False,
                                 help='Show the commands to set the credentials')
    argument_parser.add_argument('-r', '--refresh',
                                 action='store_true',
                                 dest='force_refresh',
                                 default=False,
                                 help='Force refresh credentials')
    argument_parser.add_argument('-l', '--list',
                                 action='store_true',
                                 default=False,
                                 dest='list_profiles',
                                 help='List information about your profiles')
    argument_parser.add_argument('--session-name',
                                 default=None,
                                 dest='session_name',
                                 metavar='session_name',
                                 help='Set a custom session name')
    argument_parser.add_argument('--install-plugin',
                                 nargs=2,
                                 dest='plugin_urls',
                                 metavar=('.py_url', '.yapsy-plugin_url'),
                                 default=None,
                                 help='Install a plugin given two urls')
    argument_parser.add_argument('--delete-plugin',
                                 nargs=1,
                                 dest='delete_plugin_name',
                                 metavar=('name_of_plugin'),
                                 default=None,
                                 help='Delete the .py and .yapsy-plugin files of the given plugin')
    argument_parser.add_argument('--rolesusers',
                                 action='store_true',
                                 default=False,
                                 dest='list_profile_names',
                                 help='List all profile names available')
    argument_parser.add_argument('--plugin-info',
                                 action='store_true',
                                 default=False,
                                 dest='display_plugin_info',
                                 help='Display information about installed plugins')
    argument_parser.add_argument('-a', '--auto-refresh',
                                 action='store_true',
                                 default=False,
                                 dest='auto_refresh',
                                 help='Auto-refresh role credentials')
    argument_parser.add_argument('-k', '--kill-refreshing',
                                 action='store_true',
                                 default=False,
                                 dest='kill',
                                 help='Kill autoawsume')
    argument_parser.add_argument('--info',
                                 action='store_true',
                                 dest='info',
                                 help='Print any info logs to stderr')
    argument_parser.add_argument('--debug',
                                 action='store_true',
                                 dest='debug',
                                 help='Print any debug logs to stderr')
    return argument_parser

def parse_args(argument_parser, system_arguments):
    """Call `parse_args` on the argument parser.

    Parameters
    ----------
    - argument_parser - the main argument parser for awsume
    - system_arguments - the arguments from the system

    Returns
    -------
    The parsed arguments.
    """
    return argument_parser.parse_args(system_arguments)



#
#   ReadAWSFiles
#
def read_ini_file(file_path):
    """Read an ini file and return the profile data.
    If the profile name begins with 'profile ', remove it.

    Parameters
    ----------
    - file_path - the path to the file to read

    Returns
    -------
    The profile data.
    """
    LOG.info('Reading ini file from %s', file_path)

    profiles = {}
    if os.path.exists(file_path):
        parser = ConfigParser.ConfigParser()
        parser.read(file_path)
        for profile in parser.sections():
            profiles[profile.replace('profile ', '')] = {}
            profiles[profile.replace('profile ', '')]['__name__'] = profile.replace('profile ', '')
            for option in parser.options(profile):
                profiles[profile.replace('profile ', '')][option] = parser.get(profile, option)
    else:
        safe_print('AWSume Error: Directory [' + file_path + '] does not exist')
    return profiles

def merge_role_and_source_profile(role_profile, source_profile):
    """Merge the two profiles together to create a role/source profile combination.
    The merged profile should be within the role_profile

    Parameters
    ----------
    - role_profile - a role profile
    - source_profile - the role_profile's source_profile
    """
    LOG.info('merging config and credentials profile for [%s]', role_profile['__name__'])
    LOG.debug('Role profile: %s', json.dumps(role_profile, indent=2))
    LOG.debug('Source profile: %s', json.dumps(source_profile, indent=2))
    if valid_profile(source_profile):
        role_profile['aws_access_key_id'] = source_profile['aws_access_key_id']
        role_profile['aws_secret_access_key'] = source_profile['aws_secret_access_key']
        if 'mfa_serial' not in role_profile and 'mfa_serial' in source_profile:
            role_profile['mfa_serial'] = source_profile['mfa_serial']
        if 'region' not in role_profile and 'region' in source_profile:
            role_profile['region'] = source_profile['region']

def mix_role_and_source_profiles(profiles):
    """For any role profile in `profiles`,
    add the aws_access_key_id and the aws_secret_access_key
    from the source_profile to the role profile.

    Parameters
    ----------
    - profiles - the collected aws profiles

    Returns
    -------
    A dict of aws profiles with the roles combined with their source_profiles
    """
    LOG.info('Combining role and source profiles')
    for profile in profiles:
        if is_role(profiles[profile]):
            source_profile_name = profiles[profile]['source_profile']
            if profiles.get(source_profile_name):
                merge_role_and_source_profile(profiles[profile], profiles[source_profile_name])
            else:
                safe_print('AWSume profile configuration error: Source Profile [{}] for profile [{}] doesn\'t exist'.format(source_profile_name, profile))
                exit(0)

def get_aws_profiles(app, args, config_file_path, credentials_file_path):
    """Read the aws files and create dicts of the file data.

    Parameters
    ----------
    - app - the AWSume app object
    - args - the commandline arguments
    - config_file_path - the path to the config file
    - credentials_file_path - the path to the credentials file

    Returns
    -------
    A dict of the aws files.
    """
    LOG.info('Getting AWS profiles')
    LOG.debug('Config path: %s', config_file_path)
    LOG.debug('Credentials path: %s', credentials_file_path)

    config_profiles = read_ini_file(config_file_path)
    credentials_profiles = read_ini_file(credentials_file_path)
    trim_auto_profiles(credentials_profiles)
    combined_profiles = {}
    profile_names = list(config_profiles.keys()) + list(credentials_profiles.keys())

    for profile in set(profile_names):
        combined_profiles[profile] = {}
        if profile in credentials_profiles:
            combined_profiles[profile].update(credentials_profiles[profile])
        if profile in config_profiles:
            combined_profiles[profile].update(config_profiles[profile])
    return combined_profiles

def get_aws_profiles_callback(app, args, profiles): # pragma: no cover
    """Execute what needs to be done right after the profiles are collected.

    Parameters
    ----------
    - app - the AWSume app object
    - args - the commandline arguments
    - profiles - the collected aws profiles
    """
    LOG.info('Validating Profile')
    # list profiles
    if args.list_profiles is True:
        LOG.debug('Listing profile data')
        list_profile_data(profiles)
        exit(0)
    try:
        profile = profiles.get(args.target_profile_name)
        if profile is None:
            safe_print('AWSume error: Profile not found')
            raise ProfileNotFoundError
        else:
            if not valid_profile(profile):
                safe_print('AWSume error: Invalid profile')
                raise InvalidProfileError
    except ProfileNotFoundError:
        LOG.debug('Profile not found')
        if app.awsumeFunctions['catch_profile_not_found']:
            for func in app.awsumeFunctions['catch_profile_not_found']:
                func(app, args, profiles)
        else:
            exit(0)
    except InvalidProfileError:
        LOG.debug('Profile is invalid')
        if app.awsumeFunctions['catch_invalid_profile']:
            for func in app.awsumeFunctions['catch_invalid_profile']:
                func(app, args, profiles, profile)
        else:
            exit(0)

def trim_auto_profiles(profiles):
    """Remove any profiles in the given `profiles` dict that are autoawsume profiles.

    Parameters
    ----------
    - profiles - the collected aws profiles
    """
    LOG.debug('Removing auto-refresh- profiles')
    for profile in list(profiles):
        if 'auto-refresh-' in profile:
            profiles.pop(profile)



#
#   Listing Profiles
#
def get_account_id(profile):
    """Return the account ID of the given profile if available.

    Parameters
    ----------
    - profile - an aws profile

    Returns
    -------
    A string containing the aws account ID of the given profile
    if it is available, else return 'Unavailable'.
    """
    LOG.info('Getting account ID from profile: %s', json.dumps(profile, indent=2))
    if profile.get('role_arn'):
        return profile['role_arn'].replace('arn:aws:iam::', '').split(':')[0]
    if profile.get('mfa_serial'):
        return profile['mfa_serial'].replace('arn:aws:iam::', '').split(':')[0]
    return 'Unavailable'

def format_aws_profiles(profiles):
    """Format the aws profiles for easy printing.

    Parameters
    ----------
    - profiles - the collected aws profiles

    Returns
    -------
    A well formatted list that makes it easy to print.
    The first element in the list is a list of column headers.
    The following elements in the list contain aws profile data,
    one element per profile.
    """
    LOG.info('Generating print-friendly profile data')

    sorted_profiles = collections.OrderedDict(sorted(profiles.items()))

    # List headers
    list_headers = ['PROFILE', 'TYPE', 'SOURCE', 'MFA?', 'REGION', 'ACCOUNT']
    profile_list = []
    profile_list.append([])
    profile_list[0].extend(list_headers)
    #now fill the tables with the appropriate data
    for name in sorted_profiles:
        #don't add any autoawsume profiles
        if 'auto-refresh-' not in name:
            profile = sorted_profiles[name]
            is_role_profile = is_role(profile)
            profile_type = 'Role' if is_role_profile else 'User'
            source_profile = profile['source_profile'] if is_role_profile else 'None'
            mfa_needed = 'Yes' if 'mfa_serial' in profile else 'No'
            profile_region = str(profile.get('region'))
            profile_account_id = get_account_id(profile)
            list_row = [name, profile_type, source_profile, mfa_needed, profile_region, profile_account_id]
            profile_list.append(list_row)
    return profile_list

def print_formatted_data(profile_data): # pragma: no cover
    """Print the given profile data.

    Parameters
    ----------
    - profile_data - the list of profile data that's returned from `format_aws_profiles`
    """
    LOG.info('Printing formatted profile data')
    print('Listing...\n')

    widths = [max(map(len, col)) for col in zip(*profile_data)]
    print('AWS Profiles'.center(sum(widths) + 10, '='))
    for row in profile_data:
        print('  '.join((val.ljust(width) for val, width in zip(row, widths))))

def list_profile_data(profiles):
    """List useful information about the collected aws profiles.

    Parameters
    ----------
    - profiles - the collected aws profiles
    """
    LOG.info('Listing aws profiles')

    formatted_profiles = format_aws_profiles(profiles)
    print_formatted_data(formatted_profiles)

def get_profile_names(args, app):
    """Get a list of all awsume-able profile names

    Parameters
    ----------
    - args - the commandline args
    - app - the AWSume app object

    Returns
    -------
    A list of profile names
    """
    LOG.info('Getting profile names')
    profiles = {}
    profiles = get_aws_profiles(app, args, AWS_CONFIG_FILE, AWS_CREDENTIALS_FILE)
    mix_role_and_source_profiles(profiles)
    profile_names = []
    for profile in profiles:
        profile_names.append(profile)
    return profile_names

def list_profile_names(args, app):
    """Handle listProfilenames argument flag. Print a list of profile names.

    Parameters
    ----------
    - args - the commandline arguments
    - app - the AWSume app object
    """
    LOG.info('Listing profile names')
    profile_names = []
    for func in app.awsumeFunctions['get_profile_names']:
        profile_names.extend(func(args, app))
    print('\n'.join(profile_names))

#
#   InspectionAndValidation
#
def valid_profile(profile):
    """Checks to see if the given profile is valid.
    A profile is valid if it is either:
      - a non-role profile with both aws_access_key_id and aws_secret_access_key
      - a valid role profile

    Parameters
    ----------
    - profile - the profile to inspect

    Returns
    -------
    True if the profile is valid, False if it isn't.
    """
    LOG.debug('Checking profile validity: %s', json.dumps(profile, indent=2))
    if all(key in profile for key in ['aws_access_key_id', 'aws_secret_access_key']):
        return True
    if is_role(profile):
        return True
    LOG.debug('Invalid profile:\n%s', json.dumps(profile, default=str, indent=2))
    return False

def requires_mfa(profile):
    """Checks to see if the given profile requires MFA.

    Parameters
    ----------
    - profile - the profile to inspect

    Returns
    -------
    True if the profile requires MFA, False if it doesn't.
    """
    return 'mfa_serial' in profile

def is_role(profile):
    """Checks to see if the given profile is a role profile.
    A profile is a role profile if it contains a 'role_arn' and a 'source_profile'.

    Parameters
    ----------
    - profile - the profile to inspect

    Returns
    -------
    True if the profile is a role profile, False if it doesn't.
    """
    if 'source_profile' in profile and 'role_arn' in profile:
        return True
    return False

def valid_mfa_token(token):
    """Checks to see if the given mfa token is a valid 6-digit mfa token.

    Parameters
    ----------
    - token - the token to validate

    Returns
    -------
    True if the given token is a valid mfa token, False if it isn't.
    """
    LOG.debug('Validating MFA token: %s', token)
    token_pattern = re.compile('^[0-9]{6}$')
    if not token_pattern.match(token):
        LOG.debug('%s is not a valid mfa token', token)
        return False
    return True

def valid_cache_session(session):
    """Determine if the given session is valid.
    Check if it is expired.

    Parameters
    ----------
    - session - the session to verify

    Returns
    -------
    True if the session is valid, false if it isn't.
    """
    LOG.info('Validating cache session')
    LOG.debug(session)
    try:
        session_expiration = datetime.strptime(session['Expiration'], '%Y-%m-%d %H:%M:%S')
        if session_expiration > datetime.now():
            return True
        LOG.debug('Session is expired')
    except Exception:
        LOG.debug('Session is invalid')
    return False

def fix_session_credentials(session, profiles, args):
    """Format the given session.
    In particular fix the expiration to be of local timezone.

    Parameters
    ----------
    - session - the session credentials from the get_session_token api call
    - profiles - the collected aws profiles
    - args - the commandline args
    """
    LOG.debug('Converting session expiration to local timezone')
    session['Expiration'] = session['Expiration'].astimezone(dateutil.tz.tzlocal())
    session['Expiration'] = session['Expiration'].strftime('%Y-%m-%d %H:%M:%S')

    region = profiles[args.target_profile_name].get('region')
    if not region and profiles.get('default'):
        LOG.debug('region not found in profile, using default profile\'s region')
        region = profiles['default'].get('region')
    session['region'] = region



#
#   Input/Output
#
def get_input(): # pragma: no cover
    """A simple wrapper around the `read_input` python function.

    Returns
    -------
    The value returned from `read_input()`.
    """
    return read_input()

def safe_print(text, end=None): # pragma: no cover
    """A simple wrapper around the builting `print` function.
    It should always print to stderr to not interfere with the shell wrappers.

    Parameters
    ----------
    - text - the text to print
    """
    print(text, file=sys.stderr, end=end)

def read_mfa():
    """Read mfa from the command line.
    If token is invalid, retry.

    Returns
    -------
    The read mfa token.
    """
    safe_print('Enter MFA token: ', end='')
    while True:
        mfa_token = get_input()
        if valid_mfa_token(mfa_token):
            return mfa_token
        else:
            safe_print('Please enter a valid MFA token: ', end='')



#
#   Caching sessions
#
def read_aws_cache(cache_path, cache_name):
    """Read the aws cache file.

    Parameters
    ----------
    - cache_path - the path to the aws cache directory
    - cache_name - the name of the cache file

    Returns
    -------
    The read credentials object if the file exists, {} if it doesn't.
    """
    LOG.info('Reading aws cache file')
    try:
        if os.path.isfile(cache_path + cache_name):
            LOG.debug('cache file exists, loading it')
            session = json.load(open(cache_path + cache_name))
            return session
        LOG.debug('cache file does not exist')
        return {}
    except Exception as exception:
        LOG.debug('Exception when reading cache: %s', exception)
        return {}

def write_aws_cache(cache_path, cache_name, session):
    """Write the session to a file.

    Parameters
    ----------
    - cache_path - the path to the aws cache directory
    - cache_name - the name of the cache file
    - session - the session to write
    """
    LOG.info('writing aws cache session')
    LOG.debug('session to cache: %s', json.dumps(session, indent=2))
    if not os.path.exists(cache_path):
        LOG.debug('cache directory does not exist, making it')
        os.makedirs(cache_path)
    json.dump(session, open(cache_path + cache_name, 'w'), indent=2, default=str)



#
#   AWSume workflow
#
def pre_awsume(app, args):
    """Execute anything that needs to be handled before awsume.
    Check for any specific flags and handle them accordingly.
    Set the `target_profile_name`. If `profile_name` is none, target the default profile.

    Parameters
    ----------
    - app - the AWSume app object
    - args - the commandline arguments
    """
    LOG.info('Preparing to run the AWSume workflow')

    if args.info: # pragma: no cover
        LOG.setLevel(logging.INFO)
        LOG.info('Info logs are visible')
    if args.debug: # pragma: no cover
        LOG.setLevel(logging.DEBUG)
        LOG.debug('Debug logs are visible')

    if args.profile_name is None:
        LOG.debug('Profilename not given, using default')
        args.target_profile_name = 'default'
    else:
        LOG.debug('Using profilename: %s', args.profile_name)
        args.target_profile_name = args.profile_name

    if args.version: # pragma: no cover
        LOG.debug('version flag triggered')
        safe_print(__version__)
        exit(0)

    if args.kill:
        LOG.debug('kill flag triggered')
        kill(args, app)
        exit(0)

    if args.list_profile_names:
        LOG.debug('Listing profile names')
        list_profile_names(args, app)
        exit(0)

    if args.plugin_urls:
        LOG.debug('Installing plugin from %s', args.plugin_urls)
        download_plugin(*args.plugin_urls)
        exit(0)

    if args.delete_plugin_name:
        LOG.debug('Attempting to delete plugin: %s', args.delete_plugin_name[0])
        delete_plugin(args.delete_plugin_name[0])
        exit(0)

    if args.display_plugin_info:
        LOG.debug('displaying plugin info')
        display_plugin_info(app.plugin_manager)
        exit(0)

def create_sts_client(aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None):
    """Create a Boto3 STS client with the given credentials.

    Parameters
    ----------
    - aws_access_key_id - the access key id that will be used to create the client
    - aws_secret_access_key - the secret access key that will be used to create the client
    - aws_session_token - the session token that will be used to create the client

    Returns
    -------
    A Boto3 STS client.
    """
    LOG.info('Creating an STS client')
    sts_client = boto3.client('sts',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              aws_session_token=aws_session_token)
    return sts_client

def get_user_session(app, args, profiles, cache_path, user_session):
    """Call get-session-token to get the user session credentials.
    If the profile is a user profile that doesn't require MFA (just an aws_access_key_id and
    an aws_secret_access_key), then return the credentials without a session token.

    Parameters
    ----------
    - app - the AWSume app object
    - args - the command-line args
    - profiles - the collected aws profiles
    - cache_path - the directory to the cache file
    - user_session - the state of the previously called get_user_session

    Returns
    -------
    The session credentials from the get-session-token api call.
    """
    LOG.info('Getting user session credentials')
    profile = profiles[args.target_profile_name]
    if not is_role(profile) and not requires_mfa(profile):
        LOG.debug('Profile is a user that does not require MFA')
        credentials = {
            'AccessKeyId' : profile.get('aws_access_key_id'),
            'SecretAccessKey' : profile.get('aws_secret_access_key'),
            'region' : profile.get('region')
        }
        return credentials

    cache_file_name = 'awsume-credentials-'
    cache_file_name += args.target_profile_name if not is_role(profile) else profile['source_profile']
    cache_session = read_aws_cache(cache_path, cache_file_name)
    if args.force_refresh is False and valid_cache_session(cache_session):
        LOG.debug('returning cache session: %s', json.dumps(cache_session, indent=2))
        return cache_session

    sts_client = create_sts_client(profile['aws_access_key_id'], profile['aws_secret_access_key'])
    if requires_mfa(profile):
        LOG.debug('profile requires mfa')
        mfa_token = read_mfa()
        try:
            response = sts_client.get_session_token(SerialNumber=profile['mfa_serial'],
                                                    TokenCode=mfa_token)
            fix_session_credentials(response['Credentials'], profiles, args)
            LOG.debug(response['Credentials'])
            write_aws_cache(cache_path, cache_file_name, response['Credentials'])
            return response['Credentials']
        except botocore.exceptions.ClientError as exception:
            safe_print('AWSume error: ' + exception.response['Error']['Message'])
            raise UserAuthenticationError
    else:
        LOG.debug('profile does not require mfa')
        try:
            response = sts_client.get_session_token()
            fix_session_credentials(response['Credentials'], profiles, args)
            LOG.debug(response['Credentials'])
            return response['Credentials']
        except botocore.exceptions.ClientError as exception:
            safe_print('AWSume error: ' + exception.response['Error']['Message'])
            raise UserAuthenticationError

def get_role_session(app, args, profiles, user_session, role_session):
    """Call assume-role to get the role session credentials.

    Parameters
    ----------
    - app - the AWSume app object
    - args - the command-line arguments
    - profiles - the collected aws profiles
    - user_session - the user session credentials
    - role_session - the state of the previously called get_role_session

    Returns
    -------
    The session credentials from the assume-role api call
    """
    LOG.info('Getting role session credentials')
    profile = profiles[args.target_profile_name]
    if args.session_name:
        LOG.debug('using custom session name: %s', args.session_name)
        role_session_name = args.session_name
    else:
        role_session_name = 'awsume-session-' + args.target_profile_name
    sts_client = create_sts_client(user_session['AccessKeyId'],
                                   user_session['SecretAccessKey'],
                                   user_session['SessionToken'])

    try:
        response = sts_client.assume_role(RoleArn=profile['role_arn'],
                                          RoleSessionName=role_session_name)
        fix_session_credentials(response['Credentials'], profiles, args)
        LOG.debug(response['Credentials'])
        return response['Credentials']
    except botocore.exceptions.ClientError as exception:
        safe_print('AWSume error: ' + exception.response['Error']['Message'])
        raise RoleAuthenticationError

def get_role_session_callback(app, args, profiles, user_session, role_session): # pragma: no cover
    """Call assume-role to get the role session credentials.

    Parameters
    ----------
    - app - the AWSume app object
    - args - the command-line args
    - profiles - the collected aws profiles
    - user_session - the user session credentials
    - role_session - the state of the previously called get_role_session
    """
    if args.auto_refresh:
        LOG.debug('starting auto refresher')
        start_auto_awsume(args, app, profiles, AWS_CREDENTIALS_FILE, user_session, role_session)



#
#   AutoAwsume
#
def start_auto_awsume(args, app, profiles, credentials_file_path, user_session, role_session):
    """Start autoawsume.

    Parameters
    ----------
    - args - the commandline args
    - app - the AWSume app object
    - profiles - the collected aws profiles
    - credentials_file_path - the path to the credentials file
    - user_session - the session credentials from the get-session-token api call
    - role_session - the session credentials from the assume-role api call
    """
    LOG.info('starting auto refresher')
    profile = profiles[args.target_profile_name]
    if args.session_name:
        role_session_name = args.session_name
        LOG.debug('custom session name: %s', role_session_name)
    else:
        role_session_name = 'awsume-session-' + args.target_profile_name
        LOG.debug('default session name: %s', role_session_name)
    auto_profile = create_auto_profile(role_session,
                                       user_session,
                                       role_session_name,
                                       profile['source_profile'],
                                       profile['role_arn'])
    write_auto_awsume_session(args.target_profile_name, auto_profile, credentials_file_path)
    kill_all_auto_processes()
    data_list = [
        str('auto-refresh-' + args.target_profile_name),
        str(role_session['region']),
        str(args.target_profile_name)
    ]
    data = {
        'AWSUME_FLAG' : 'Auto',
        'AWSUME_LIST' : data_list
    }
    app.set_export_data(data)

def is_auto_profiles(credentials_file_path=AWS_CREDENTIALS_FILE):
    """Return whether or not there are auto-refresh- profiles in the credentials file.

    Parameters
    ----------
    - credentials_file_path - the path to the aws credentials file

    Returns
    -------
    True if there are auto-refresh- profiles, False if there aren't
    """
    LOG.info('checking for auto-refresh- profiles in the credentials file')
    auto_awsume_parser = ConfigParser.ConfigParser()
    auto_awsume_parser.read(credentials_file_path)
    for profile in auto_awsume_parser.sections():
        if 'auto-refresh-' in profile:
            return True
    return False

def remove_auto_profile(profile_name=None):
    """Remove the given profile from the credentials file.
    Prefix `profile_name` with 'auto-refresh-' so that we wont delete non-autoawsume profiles.
    If `profile_name` is none, remove all auto profiles.

    Parameters
    ----------
    - profile - the profile that must be removed from the credentials file
    """
    auto_awsume_parser = ConfigParser.ConfigParser()
    auto_awsume_parser.read(AWS_CREDENTIALS_FILE)
    if profile_name:
        LOG.debug('removing auto-refresh- profile: %s', profile_name)
        auto_profile_name = 'auto-refresh-' + profile_name
        if auto_awsume_parser.has_section(auto_profile_name):
            auto_awsume_parser.remove_section(auto_profile_name)
    else:
        LOG.debug('removing all auto-refresh- profiles')
        for profile in auto_awsume_parser.sections():
            if 'auto-refresh-' in profile:
                LOG.debug('removing auto-refresh- profile: %s', profile)
                auto_awsume_parser.remove_section(profile)
    auto_awsume_parser.write(open(AWS_CREDENTIALS_FILE, 'w'))

def write_auto_awsume_session(profile_name, auto_profile, credentials_file_path):
    """Write the auto-refresh- profile to the credentials file.

    Parameters
    ----------
    - auto_profile - the profile to be written
    - credentials_file_path - the path to the credentials file
    """
    LOG.info('Writing auto-awsume session')
    LOG.debug('Profile name: %s', profile_name)
    LOG.debug('AutoAwsume profile: %s', json.dumps(auto_profile, indent=2))
    auto_profile_name = 'auto-refresh-' + profile_name
    auto_awsume_parser = ConfigParser.ConfigParser()
    auto_awsume_parser.read(credentials_file_path)
    if auto_awsume_parser.has_section(auto_profile_name):
        auto_awsume_parser.remove_section(auto_profile_name)
    auto_awsume_parser.add_section(auto_profile_name)
    for key in auto_profile:
        auto_awsume_parser.set(auto_profile_name, key, str(auto_profile.get(key)))
    auto_awsume_parser.write(open(credentials_file_path, 'w'))

def create_auto_profile(role_session, user_session, session_name, source_profile_name, role_arn):
    """Create the profile that'll be stored in the credentials file for autoawsume.

    Parameters
    ----------
    - role_session - the session credentials from the assume-role api call
    - user_session - the session credentials from the get-session-token api call
    - session_name - the name to give to the role session
    - source_profile_name - the name of the source profile

    Returns
    -------
    The autoawsume profile
    """
    return {
        'aws_access_key_id' : role_session['AccessKeyId'],
        'aws_secret_access_key' : role_session['SecretAccessKey'],
        'aws_session_token' : role_session['SessionToken'],
        'aws_region' : role_session['region'],
        'awsume_role_expiration' : role_session['Expiration'],
        'awsume_user_expiration' : user_session['Expiration'],
        'awsume_session_name' : session_name,
        'awsume_cache_name' : 'awsume-credentials-' + source_profile_name,
        'aws_role_arn' : role_arn,
    }

def kill_all_auto_processes():
    """Kill all running autoawsume processes."""
    LOG.info('Killing all autoawsume processes')

    for proc in psutil.process_iter():
        try:
            for command_string in proc.cmdline():
                if 'autoawsume' in command_string:
                    LOG.debug('Found an autoawsume process, killing it')
                    proc.kill()
        except Exception:
            pass

def kill(args, app):
    """Handle the kill flag.

    Parameters
    ----------
    - args - the command-line arguments
    - app - the AWSume app object
    """
    if args.profile_name:
        LOG.debug('Will no longer auto refresh profile: %s', args.profile_name)
        remove_auto_profile(args.profile_name)
        if not is_auto_profiles(AWS_CREDENTIALS_FILE):
            LOG.debug('No profiles left to refresh, ')
            kill_all_auto_processes()
        else:
            app.set_export_data({'AWSUME_FLAG' : 'Stop', 'AWSUME_LIST': [args.profile_name]})
            app.export_data()
            return
    else:
        LOG.debug('Killing auto-refresher, no longer refreshing any profiles.')
        kill_all_auto_processes()
        remove_auto_profile()
    app.set_export_data({'AWSUME_FLAG' : 'Kill', 'AWSUME_LIST' : []})
    app.export_data()



#
#   Plugin Management
#
def get_main_content_type(url_info):
    """Return the main content type of an HTTPMessage object in a Python 2 and 3 compatible way.

    Parameters
    ----------
    - url_info - the HTTPMessage object

    Returns
    -------
    a string containing the main content type
    """
    try: # Python 3
        return url_info.get_content_maintype()
    except AttributeError: # Python 2
        return url_info.getmaintype()

def download_file(url):
    """Download a file from the given url and return a string of it's contents

    Parameters
    ----------
    - url - the url to the file to download

    Returns
    -------
    a string of the file contents
    """
    response = six.moves.urllib.request.urlopen(url)
    content_type = get_main_content_type(response.info())
    if content_type != 'text' and content_type != 'binary':
        safe_print('AWSume error: The file needs to be a plain text file, received [' + str(content_type) + ']')
        raise Exception
    download = response.read()
    return download.decode('utf-8')

def write_plugin_files(file1, file2, filename1, filename2):
    """Write the given files to the plugin directory.

    Parameters
    ----------
    - file1 - the contents of the first plugin file
    - file2 - the contents of the second plugin file
    - filename1 - the name of the first plugin file
    - filename2 - the name of the second plugin file
    """
    filepath1 = os.path.join(AWSUME_PLUGIN_DIRECTORY, filename1)
    filepath2 = os.path.join(AWSUME_PLUGIN_DIRECTORY, filename2)

    if os.path.isfile(filepath1) or os.path.isfile(filepath2):
        safe_print('It looks like that plugin is already installed, would you like to overwrite it? (y/N) : ', end='')
        choice = get_input()
        if not choice.startswith('y') and not choice.startswith('Y'):
            return
    safe_print('Saving ' + filename1 + ' and ' + filename2 + ' to ' + AWSUME_PLUGIN_DIRECTORY)
    with open(filepath1, 'w') as writefile:
        writefile.write(file1)
    with open(filepath2, 'w') as writefile:
        writefile.write(file2)

def download_plugin(url1, url2):
    """Download the plugin from the given url. There should be two downloads: one .py file and one .yapsy-plugin file.

    Parameters
    ----------
    - url1 - ideally the url to the .py file, but could be switched
    - url2 - ideally the url to the .yapsy-plugin file, but could be switched
    """
    LOG.info('Downloading plugins')
    url1 = url1.replace('\\', '/')
    url2 = url2.replace('\\', '/')
    filename1 = url1.split('?')[0].split('/')[-1]
    filename2 = url2.split('?')[0].split('/')[-1]

    if not filename1 or not filename2:
        safe_print('AWSume error: Please provide a url to a valid file.')
        return

    if not (filename1.endswith('.py') and filename2.endswith('.yapsy-plugin') or
            filename1.endswith('.yapsy-plugin') and filename2.endswith('.py')):
        safe_print('AWSume error: Please supply urls to one .py file and one .yapsy-plugin file')
        return
    if filename1 == url1 and filename2 == url2:
        cache = read_plugin_cache()
        if cache.get(filename1) and cache.get(filename2):
            url1 = cache[filename1]
            url2 = cache[filename2]
    try:
        LOG.debug('Downloading from %s', url1)
        file1 = download_file(url1)
        LOG.debug('Downloading from %s', url2)
        file2 = download_file(url2)
    except Exception as exception:
        safe_print('AWSume error: Could not download files: ' + str(exception))
        return

    write_plugin_files(file1, file2, filename1, filename2)
    cache_urls(url1, url2, filename1, filename2)

def delete_plugin(plugin_name):
    """Delete the .py and .yapsy-plugin file given by `plugin_name` from the plugins directory.

    Parameters
    ----------
    - plugin_name - the name of the plugin to delete
    """

    directory = os.listdir(AWSUME_PLUGIN_DIRECTORY)
    plugins = [item for item in directory if item.endswith('.yapsy-plugin')]
    plugins = [name.split('.yapsy-plugin')[0] for name in plugins]
    if plugin_name not in plugins:
        safe_print('That plugin doesn\'t exist')
        return

    plugin_files = [item for item in directory if plugin_name in item]
    safe_print('All plugin files will be deleted, are you sure you want to delete the plugin: [' + plugin_name + ']')
    safe_print('\n'.join(plugin_files))
    safe_print('(y/N)? ', end='')
    choice = get_input()
    if not choice.startswith('y') and not choice.startswith('Y'):
        return
    for item in plugin_files:
        item_path = os.path.join(AWSUME_PLUGIN_DIRECTORY, item)
        if os.path.isfile(item_path):
            safe_print('Deleting file: ' + item)
            os.remove(item_path)
        elif os.path.isdir(item_path):
            safe_print('Deleting directory and contents: ' + item)
            shutil.rmtree(item_path)

def read_plugin_cache():
    """Read the plugin cache.

    Returns
    -------
    The cache'd object.
    """
    if os.path.isfile(AWSUME_PLUGIN_CACHE_FILE):
        try:
            return json.load(open(AWSUME_PLUGIN_CACHE_FILE, 'r'))
        except Exception:
            json.dump({}, open(AWSUME_PLUGIN_CACHE_FILE, 'w'))
    return {}

def cache_urls(url1, url2, filename1, filename2):
    """Cache the plugin urls for the given `plugin_name`

    Parameters
    ----------
    - url1 - one of the urls to the plugin
    - url2 - one of the urls to the plugin
    - filename1 - the name to remember url1 as
    - filename2 - the name to remember url2 as
    """
    cache = read_plugin_cache()
    cache[filename1] = url1
    cache[filename2] = url2
    json.dump(cache, open(AWSUME_PLUGIN_CACHE_FILE, 'w'), indent=2)

def display_plugin_info(manager):
    """Display useful information about installed plugins

    Parameters
    ----------
    - manager - the plugin manager
    """
    cache = read_plugin_cache()
    if cache:
        safe_print('')
        safe_print('===== Cached Plugins =====')
        for filename in cache:
            safe_print(filename + ' ->')
            safe_print('  ' + cache[filename])
        safe_print('===== Cached Plugins =====')

    plugins = manager.getAllPlugins()
    if plugins:
        for plugin in manager.getAllPlugins():
            safe_print('')
            safe_print('Name: ' + plugin.name)
            safe_print('Author: ' + plugin.author)
            safe_print('Version: ' + str(plugin.version))
            safe_print('Website: ' + plugin.website)
            safe_print('Description: ' + plugin.description)
    else:
        safe_print('AWSume: You do not have any installed plugins.')



#
#   AWSume App
#
def create_plugin_manager(plugin_directory):
    """Create the plugin manager, set the location to look for the plugins, and collect them."""
    plugin_manager = PluginManager.PluginManager()
    plugin_manager.setPluginPlaces([plugin_directory])
    try:
        plugin_manager.collectPlugins()
    except Exception as exception:
        safe_print('AWSume error: Unable to collect plugins: ' + str(exception))
        return None
    return plugin_manager

def register_plugins(app, manager):
    """Register all available plugins from the manager.

    Parameters
    ----------
    - app - the AWSume app object
    - manager - a yapsy plugin manager
    """
    for plugin in manager.getAllPlugins():
        try:
            if plugin.plugin_object.TARGET_VERSION.split('.')[0] != __version__.split('.')[0]:
                safe_print('AWSume warning: [{}] targets AWSume version {}'.format(plugin.name, plugin.plugin_object.TARGET_VERSION))
        except AttributeError:
            safe_print('AWSume warning: [{}] has no targeted version. AWSume may not work as expected.'.format(plugin.name))

        for function_type in app.validFunctions:
            if function_type in dir(plugin.plugin_object):
                if not app.register_function(function_type, getattr(plugin.plugin_object, function_type)):
                    safe_print('Unable to  register plugin [{}] function of type {}'.format(plugin.name, function_type))

class AwsumeApp(object):
    """The app that runs AWSume."""
    awsumeFunctions = {}
    validFunctions = [
        'add_arguments',
        'pre_awsume',
        'get_aws_profiles',
        'get_aws_profiles_callback',
        'get_user_session',
        'get_user_session_callback',
        'get_role_session',
        'get_role_session_callback',
        'post_awsume',
        'catch_profile_not_found',
        'catch_invalid_profile',
        'catch_user_authentication_error',
        'catch_role_authentication_error',
        'get_profile_names',
    ]
    __out_data = {
        'AWSUME_FLAG':'',
        'AWSUME_LIST':[],
        'exported':False,
    }

    def __init__(self, plugin_manager): # pragma: no cover
        """Create plugin function types, add defaults to the lists.

        Parameters
        ----------
        - plugin_manager - the main plugin manager
        """
        for directory in [AWS_DIRECTORY, AWSUME_PLUGIN_DIRECTORY]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        for filename in [AWS_CREDENTIALS_FILE, AWS_CONFIG_FILE]:
            if not os.path.isfile(filename):
                open(filename, 'a').close()
        self.plugin_manager = plugin_manager
        for function_type in self.validFunctions:
            self.awsumeFunctions[function_type] = []
            if globals().get(function_type):
                self.register_function(function_type, globals()[function_type])

    def register_function(self, function_type, new_function):
        """Register functions to the AWSume App.

        Returns
        -------
        True if the function was successfully registered, False if it wasn't.
        """
        if function_type in self.validFunctions:
            self.awsumeFunctions[function_type].append(new_function)
            return True
        return False

    def set_export_data(self, data):
        """Set the data that will be exported to the shell wrappers.
        If data has already been exported, ignore any future data.

        Parameters
        ----------
        - data - the data to set to be exported, should be a dict with keys:
          - AWSUME_FLAG - a string that tells the shell wrapper what to do
          - AWSUME_LIST - the data that needs to be sent to the shell wrapper
        """
        if not self.__out_data['exported']:
            LOG.debug('Data to be sent to the shell wrapper:\n%s', json.dumps(data, default=str, indent=2))
            self.__out_data['AWSUME_FLAG'] = data.get('AWSUME_FLAG')
            self.__out_data['AWSUME_LIST'] = data.get('AWSUME_LIST')
            self.__out_data['exported'] = True

    def export_data(self):
        """Print the data, sending the session to the shell wrapper."""
        LOG.debug('Exporting data to shell wrapper')
        print(str(self.__out_data['AWSUME_FLAG']), end=' ')
        print(' '.join(self.__out_data['AWSUME_LIST']))

    def run(self, system_arguments):
        """Execute AWSume."""
        argument_parser = generate_argument_parser()
        for func in self.awsumeFunctions['add_arguments']:
            func(argument_parser)
        arguments = parse_args(argument_parser, system_arguments)

        for func in self.awsumeFunctions['pre_awsume']:
            func(self, arguments)

        profiles = {}
        for func in self.awsumeFunctions['get_aws_profiles']:
            new_profiles = func(self, arguments, AWS_CONFIG_FILE, AWS_CREDENTIALS_FILE)
            profiles.update(new_profiles)
        mix_role_and_source_profiles(profiles)
        LOG.debug('Collected aws profiles:\n%s', json.dumps(profiles, default=str, indent=2))
        for func in self.awsumeFunctions['get_aws_profiles_callback']:
            func(self, arguments, profiles)

        user_session = None
        try:
            for func in self.awsumeFunctions['get_user_session']:
                user_session = func(self, arguments, profiles, AWS_CACHE_DIRECTORY, user_session)
            LOG.debug('User session:\n%s', json.dumps(user_session, default=str, indent=2))
            if user_session.get('Expiration'):
                safe_print('AWSume: User profile credentials will expire at: ' + str(user_session['Expiration']))
            for func in self.awsumeFunctions['get_user_session_callback']:
                func(self, arguments, profiles, user_session)
        except UserAuthenticationError:
            LOG.debug('UserAuthenticationError raised')
            if self.awsumeFunctions['catch_user_authentication_error']:
                for func in self.awsumeFunctions['catch_user_authentication_error']:
                    func(self, arguments, profiles)
            else:
                exit(0)
        session_to_use = user_session

        role_session = None
        try:
            if is_role(profiles[arguments.target_profile_name]):
                for func in self.awsumeFunctions['get_role_session']:
                    role_session = func(self, arguments, profiles, user_session, role_session)
                LOG.debug('Role session:\n%s', json.dumps(role_session, default=str, indent=2))
                safe_print('AWSume: Role profile credentials will expire at: ' + str(role_session['Expiration']))
                for func in self.awsumeFunctions['get_role_session_callback']:
                    func(self, arguments, profiles, user_session, role_session)
                session_to_use = role_session
        except RoleAuthenticationError:
            LOG.debug('RoleAuthenticationError raised')
            if self.awsumeFunctions['catch_role_authentication_error']:
                for func in self.awsumeFunctions['catch_role_authentication_error']:
                    func(self, arguments, profiles, user_session)
            else:
                exit(0)

        data_list = [
            str(session_to_use.get('AccessKeyId')),
            str(session_to_use.get('SecretAccessKey')),
            str(session_to_use.get('SessionToken')),
            str(session_to_use.get('region')),
            str(arguments.target_profile_name)
        ]
        data = {
            'AWSUME_FLAG' : 'Awsume',
            'AWSUME_LIST' : data_list
        }
        self.set_export_data(data)

        for func in self.awsumeFunctions['post_awsume']:
            func(self, arguments, profiles, user_session, role_session)

def main(command_line_arguments=sys.argv[1:]):
    """Create the AWSume app and plugin manager, then execute AWSume"""
    plugin_manager = create_plugin_manager(AWSUME_PLUGIN_DIRECTORY)
    awsume = AwsumeApp(plugin_manager)
    if plugin_manager:
        register_plugins(awsume, plugin_manager)
    awsume.run(command_line_arguments)
    awsume.export_data()

if __name__ == '__main__':
    main()
