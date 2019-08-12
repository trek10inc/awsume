import argparse
import configparser
import json
import colorama


from . lib.exceptions import UserAuthenticationError, RoleAuthenticationError
from . hookimpl import hookimpl
from .. import __data__
from ..autoawsume.process import kill
from . lib import aws as aws_lib
from . lib import aws_files as aws_files_lib
from . lib.logger import logger
from . lib.safe_print import safe_print
from . lib import config_management as config_lib
from . lib.exceptions import ProfileNotFoundError
from . lib import profile as profile_lib
from . lib import cache as cache_lib
from . lib.autoawsume import create_autoawsume_profile


def custom_duration_argument_type(string):
    number = int(string)
    if number >= 0 and number <= 43201:
        return number
    raise argparse.ArgumentTypeError('Custom Duration must be between 0 and 43200')


@hookimpl(tryfirst=True)
def add_arguments(config: dict, parser: argparse.ArgumentParser):
    logger.info('Adding arguments')
    parser.add_argument('-v', '--version',
        action='store_true',
        dest='version',
        help='Display the current version of awsume',
    )
    parser.add_argument('profile_name',
        nargs='?',
        action='store',
        metavar='profile_name',
        help='The target profile name',
    )
    parser.add_argument('-r', '--refresh',
        action='store_true',
        dest='force_refresh',
        help='Force refresh credentials',
    )
    parser.add_argument('-s', '--show-commands',
        action='store_true',
        dest='show_commands',
        help='Show the commands to set the credentials',
    )
    parser.add_argument('-u', '--unset',
        action='store_true',
        dest='unset_variables',
        help='Unset your aws environment variables',
    )
    parser.add_argument('-a', '--auto-refresh',
        action='store_true',
        dest='auto_refresh',
        help='Auto refresh credentials',
    )
    parser.add_argument('-k', '--kill-refresher',
        action='store_true',
        default=False,
        dest='kill',
        help='Kill autoawsume',
    )
    parser.add_argument('-l', '--list-profiles',
        nargs='?',
        action='store',
        default=None,
        const='list',
        choices=['more', 'list', None],
        metavar='more',
        dest='list_profiles',
        help='List profiles, "more" for detail (slow)',
    )
    parser.add_argument('--refresh-autocomplete',
        action='store_true',
        dest='refresh_autocomplete',
        help='Refresh all plugin autocomplete profiles',
    )
    parser.add_argument('--role-arn',
        action='store',
        dest='role_arn',
        metavar='role_arn',
        help='Role ARN to assume',
    )
    parser.add_argument('--source-profile',
        action='store',
        dest='source_profile',
        metavar='source_profile',
        help='source_profile to use (role-arn only)',
    )
    parser.add_argument('--external-id',
        action='store',
        dest='external_id',
        metavar='external_id',
        help='External ID to pass to the assume_role',
    )
    parser.add_argument('--mfa-token',
        action='store',
        dest='mfa_token',
        metavar='mfa_token',
        help='Your mfa token',
    )
    parser.add_argument('--region',
        action='store',
        dest='region',
        metavar='region',
        help='The region you want to awsume into',
    )
    parser.add_argument('--session-name',
        action='store',
        dest='session_name',
        metavar='session_name',
        help='Set a custom role session name',
    )
    parser.add_argument('--role-duration',
        action='store',
        dest='role_duration',
        type=custom_duration_argument_type,
        metavar='role_duration',
        help='Seconds to get role creds for',
    )
    assume_role_method = parser.add_mutually_exclusive_group()
    assume_role_method.add_argument('--with-saml',
        action='store_true',
        dest='with_saml',
        help='Use saml (requires plugin)',
    )
    assume_role_method.add_argument('--with-web-identity',
        action='store_true',
        dest='with_web_identity',
        help='Use web identity (requires plugin)',
    )
    parser.add_argument('--json',
        action='store',
        dest='json',
        metavar='json',
        help='Use json credentials',
    )
    parser.add_argument('--credentials-file',
        action='store',
        dest='credentials_file',
        metavar='credentials_file',
        help='Target a shared credentials file',
    )
    parser.add_argument('--config-file',
        action='store',
        dest='config_file',
        metavar='config_file',
        help='Target a config file',
    )
    parser.add_argument('--config',
        nargs='*',
        dest='config',
        action='store',
        metavar='option',
        help='Configure awsume',
    )
    parser.add_argument('--list-plugins',
        action='store_true',
        dest='list_plugins',
        help='List installed plugins',
    )
    parser.add_argument('--info',
        action='store_true',
        dest='info',
        help='Print any info logs to stderr',
    )
    parser.add_argument('--debug',
        action='store_true',
        dest='debug',
        help='Print any debug logs to stderr',
    )


@hookimpl(tryfirst=True)
def post_add_arguments(config: dict, arguments: argparse.Namespace, parser: argparse.ArgumentParser):
    logger.debug('Post add arguments')
    logger.debug(json.dumps(vars(arguments)))
    if arguments.role_arn and arguments.auto_refresh:
        safe_print('Cannot use autoawsume with given role_arn', colorama.Fore.RED)
        exit(1)
    if arguments.version:
        logger.debug('Logging version')
        safe_print(__data__.version)
        exit(0)
    if arguments.unset_variables:
        logger.debug('Unsetting environment variables')
        print('Unset', [])
        exit(0)
    if arguments.config:
        config_lib.update_config(arguments.config)
        exit(0)
    if arguments.kill:
        kill(arguments)
        exit(0)

    if arguments.role_arn and not arguments.role_arn.startswith('arn:'):
        logger.debug('Using short-hand role arn syntax')
        parts = arguments.role_arn.split(':')
        if len(parts) != 2:
            parser.error('--role-arn must be a valid role arn or follow the format "<account_id>:<role_name>"')
        if not parts[0].isnumeric() or len(parts[0]) is not 12:
            parser.error('--role-arn account id must be valid numeric account id of length 12')
        arguments.role_arn = 'arn:aws:iam::{}:role/{}'.format(parts[0], parts[1])

    if not arguments.profile_name:
        if arguments.role_arn:
            logger.debug('Role arn passed, target profile name will be role_arn')
            arguments.target_profile_name = arguments.role_arn
        else:
            logger.debug('No profile name passed, target profile name will be "default"')
            arguments.target_profile_name = 'default'
    else:
        arguments.target_profile_name = arguments.profile_name


@hookimpl(tryfirst=True)
def collect_aws_profiles(config: dict, arguments: argparse.Namespace, credentials_file: str, config_file: str):
    logger.info('Collecting AWS profiles')
    profiles = aws_files_lib.read_aws_file(credentials_file)
    config_profiles = aws_files_lib.read_aws_file(config_file)

    for profile_name, profile in config_profiles.items():
        short_name = profile_name.replace('profile ', '')
        if short_name not in profiles:
            profiles[short_name] = {}
        profiles[short_name].update(profile)
    logger.debug('Colelcted {} profiles'.format(len(profiles)))
    return profiles


@hookimpl(tryfirst=True)
def post_collect_aws_profiles(config: dict, arguments: argparse.Namespace, profiles: dict):
    logger.debug('Post collect AWS profiles')
    if arguments.list_profiles:
        logger.debug('Listing profiles')
        profile_lib.list_profile_data(profiles, arguments.list_profiles == 'more')
        exit(0)


def assume_role_from_cli(config: dict, arguments: dict, profiles: dict, region: str):
    logger.info('Using role_arn from the CLI')
    role_duration = arguments.role_duration or int(config.get('role-duration', 0))
    session_name = arguments.session_name or 'awsume-cli-role'
    logger.debug('Session name: {}'.format(session_name))
    if not arguments.source_profile:
        logger.debug('Using current credentials to assume role')
        role_session = aws_lib.assume_role({}, arguments.role_arn, session_name, region=region, external_id=arguments.external_id, role_duration=role_duration)
    else:
        logger.debug('Using the source_profile from the cli to call assume_role')
        source_profile = profiles.get(arguments.source_profile)
        if not source_profile:
            raise ProfileNotFoundError(profile_name=arguments.source_profile)
        source_credentials = profile_lib.profile_to_credentials(source_profile)
        mfa_serial = source_profile.get('mfa_serial')
        if role_duration:
            logger.debug('Using custom role duration')
            if mfa_serial:
                logger.debug('Requires MFA')
                logger.debug('Using custom role duration for role that needs mfa_serial, skipping get-session-token call')
                source_session = source_credentials
                role_session = aws_lib.assume_role(
                    source_session,
                    arguments.role_arn,
                    session_name,
                    region=region,
                    external_id=arguments.external_id,
                    role_duration=role_duration,
                    mfa_serial=mfa_serial,
                    mfa_token=arguments.mfa_token,
                )
            else:
                logger.debug('MFA not needed, assuming role from with profile creds')
                role_session = aws_lib.assume_role(
                    source_credentials,
                    arguments.role_arn,
                    session_name,
                    region=region,
                    external_id=arguments.external_id,
                    role_duration=role_duration,
                )
        else:
            logger.debug('Using default role duration')
            if mfa_serial:
                logger.debug('MFA required')
                source_session = aws_lib.get_session_token(
                    source_credentials,
                    region=profile_lib.get_region(profiles, arguments),
                    mfa_serial=mfa_serial,
                    mfa_token=arguments.mfa_token,
                    ignore_cache=arguments.force_refresh,
                )
            else:
                logger.debug('MFA not required')
                source_session = source_credentials
            role_session = aws_lib.assume_role(
                source_session,
                arguments.role_arn,
                session_name,
                region=region,
                external_id=arguments.external_id,
                role_duration=role_duration,
            )
    return role_session


@hookimpl(tryfirst=True)
def get_credentials(config: dict, arguments: argparse.Namespace, profiles: dict) -> dict:
    logger.info('Getting credentials')
    region = profile_lib.get_region(profiles, arguments)
    logger.debug('Using region: {}'.format(region))

    if arguments.role_arn:
        return assume_role_from_cli(config, arguments, profiles, region)

    target_profile = profiles.get(arguments.target_profile_name)
    profile_lib.validate_profile(profiles, arguments.target_profile_name)
    is_role = profile_lib.is_role(target_profile)
    mfa_serial = profile_lib.get_mfa_serial(profiles, arguments.target_profile_name)
    external_id = arguments.external_id or target_profile.get('external_id')
    role_duration = arguments.role_duration or target_profile.get('duration_seconds') or int(config.get('role-duration', '0'))
    if not mfa_serial:
        logger.debug('MFA is not required')
        if not is_role:
            logger.debug('No assume-role called and no mfa needed, returning profile credentials')
            return_session = profile_lib.profile_to_credentials(target_profile)
            return_session['Region'] = region
            return return_session
        else:
            logger.debug('MFA not needed, assuming role with profile credentials')
            source_profile = profile_lib.get_source_profile(profiles, arguments.target_profile_name)
            source_credentials = profile_lib.profile_to_credentials(source_profile)
            role_session = aws_lib.assume_role(
                source_credentials,
                target_profile.get('role_arn'),
                arguments.session_name or arguments.target_profile_name,
                region=region,
                external_id=external_id,
                role_duration=role_duration,
            )
            return role_session
    else:
        logger.debug('MFA is required')
        if not is_role:
            logger.debug('No assume_role call needed')
            source_credentials = profile_lib.profile_to_credentials(target_profile)
            user_session = aws_lib.get_session_token(
                source_credentials,
                region=region,
                mfa_serial=mfa_serial,
                mfa_token=arguments.mfa_token,
                ignore_cache=arguments.force_refresh,
            )
            return user_session
        else:
            logger.debug('assume_role call needed')
            if role_duration: # cannot use temp creds with custom role duration
                if arguments.auto_refresh:
                    safe_print('Cannot use autoawsume with custom role duration', colorama.Fore.RED)
                    exit(1)
                logger.debug('Skipping the get_session_token call, temp creds cannot be used for custom role duration')
                source_profile = profile_lib.get_source_profile(profiles, arguments.target_profile_name)
                source_session = profile_lib.profile_to_credentials(source_profile)
                role_session = aws_lib.assume_role(
                    source_session,
                    target_profile.get('role_arn'),
                    arguments.session_name or arguments.target_profile_name,
                    region=region,
                    external_id=external_id,
                    role_duration=role_duration,
                    mfa_serial=mfa_serial,
                    mfa_token=arguments.mfa_token,
                )
            else:
                source_profile = profile_lib.get_source_profile(profiles, arguments.target_profile_name)
                if source_profile:
                    logger.debug('Calling get_session_token to assume role with')
                    source_credentials = profile_lib.profile_to_credentials(source_profile)
                    source_session = aws_lib.get_session_token(
                        source_credentials,
                        region=region,
                        mfa_serial=mfa_serial,
                        mfa_token=arguments.mfa_token,
                        ignore_cache=arguments.force_refresh,
                    )
                elif target_profile.get('credential_source') == 'Environment':
                    logger.debug('Using environment variables')
                    source_session = {}
                role_session = aws_lib.assume_role(
                    source_session,
                    target_profile.get('role_arn'),
                    arguments.session_name or arguments.target_profile_name,
                    region=region,
                    external_id=external_id,
                    role_duration=role_duration,
                )
                if arguments.auto_refresh:
                    create_autoawsume_profile(config, arguments, role_session, source_session)
            return role_session
