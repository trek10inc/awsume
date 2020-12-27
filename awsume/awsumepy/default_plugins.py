import argparse
import configparser
import json
import os
import colorama
import subprocess
import dateutil


from . lib import exceptions
from . hookimpl import hookimpl
from .. import __data__
from ..autoawsume.process import kill
from . lib import aws as aws_lib
from . lib import aws_files as aws_files_lib
from . lib.logger import logger
from . lib.safe_print import safe_print
from . lib import config_management as config_lib
from . lib import profile as profile_lib
from . lib import cache as cache_lib
from . lib.profile import VALID_CREDENTIAL_SOURCES
from . lib.profile import get_role_chain, get_profile_name


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
    parser.add_argument('-o', '--output-profile',
        action='store',
        dest='output_profile',
        metavar='output_profile',
        help='A profile to output credentials to',
    )
    parser.add_argument('--clean',
        action='store_true',
        dest='clean',
        help='Clean expired output profiles',
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
        help='Role ARN or <partition>:<account_id>:<role_name>',
    )
    parser.add_argument('--principal-arn',
        action='store',
        dest='principal_arn',
        metavar='principal_arn',
        help='Principal ARN or <partition>:<account_id>:<provider_name>',
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
    if arguments.auto_refresh:
        if arguments.role_arn:
            raise exceptions.ValidationException('Cannot use autoawsume with a given role_arn')
        if arguments.json:
            raise exceptions.ValidationException('Cannot use autoawsume with json')
    if arguments.clean:
        _, credentials_file = aws_files_lib.get_aws_files(arguments, config)
        aws_files_lib.remove_expired_output_profiles(credentials_file)
        raise exceptions.EarlyExit()
    if arguments.version:
        logger.debug('Logging version')
        safe_print(__data__.version)
        raise exceptions.EarlyExit()
    if arguments.unset_variables:
        logger.debug('Unsetting environment variables')
        print('Unset', [])
        raise exceptions.EarlyExit()
    if type(arguments.config) is list:
        config_lib.handle_config(arguments.config)
        raise exceptions.EarlyExit()
    if arguments.kill:
        kill(arguments)
        raise exceptions.EarlyExit()

    if arguments.with_saml:
        if bool(arguments.role_arn) is not bool(arguments.principal_arn):
            parser.error('both or neither --principal-arn and --role-arn must be specified with saml')
    if not arguments.with_saml and arguments.principal_arn:
        parser.error('--principal-arn can only be specified with --with-saml')

    if arguments.role_arn and not arguments.role_arn.startswith('arn:'):
        logger.debug('Using short-hand role arn syntax')
        parts = arguments.role_arn.split(':')
        if len(parts) == 2:
            partition = 'aws'
            account_id = parts[0]
            role_name = parts[1]
        elif len(parts) == 3:
            partition = parts[0]
            account_id = parts[1]
            role_name = parts[2]
        else:
            parser.error('--role-arn must be a valid role arn or follow the format "<partition>:<account_id>:<role_name>"')
        if not account_id.isnumeric() or len(account_id) != 12:
            parser.error('--role-arn account id must be valid numeric account id of length 12')
        arguments.role_arn = 'arn:{}:iam::{}:role/{}'.format(partition, account_id, role_name)

    if arguments.principal_arn and not arguments.principal_arn.startswith('arn:'):
        logger.debug('Using short-hand role arn syntax')
        parts = arguments.principal_arn.split(':')
        if len(parts) == 2:
            partition = 'aws'
            account_id = parts[0]
            provider_name = parts[1]
        elif len(parts) == 3:
            partition = parts[0]
            account_id = parts[1]
            provider_name = parts[2]
        else:
            parser.error('--principal-arn must be a valid role arn or follow the format "<partition>:<account_id>:<provider_name>"')
        if not provider_name.isnumeric() or len(provider_name) != 12:
            parser.error('--principal-arn account id must be valid numeric account id of length 12')
        arguments.principal_arn = 'arn:{}:iam::{}:role/{}'.format(partition, account_id, provider_name)

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
    logger.debug('Collected {} profiles'.format(len(profiles)))
    return profiles


@hookimpl(tryfirst=True)
def post_collect_aws_profiles(config: dict, arguments: argparse.Namespace, profiles: dict):
    logger.info('Post collect AWS profiles')
    if arguments.list_profiles:
        logger.debug('Listing profiles')
        profiles = profile_lib.list_profile_data(profiles, arguments.list_profiles == 'more', config)
        raise exceptions.EarlyExit(data={'profiles': profiles})


def assume_role_from_cli(config: dict, arguments: dict, profiles: dict):
    region = profile_lib.get_region(profiles, arguments, config, ignore_config=True, ignore_default=True)
    logger.info('Using role_arn from the CLI')
    role_duration = arguments.role_duration or int(config.get('role-duration', 0))
    session_name = arguments.session_name or config.get('role-session-name') or 'awsume-cli-role'
    logger.debug('Session name: {}'.format(session_name))
    if not arguments.source_profile:
        logger.debug('Using current credentials to assume role')
        role_session = aws_lib.assume_role({}, arguments.role_arn, session_name, region=region, external_id=arguments.external_id, role_duration=role_duration)
    else:
        logger.debug('Using the source_profile from the cli to call assume_role')
        source_profile = profiles.get(arguments.source_profile)
        if not source_profile:
            raise exceptions.ProfileNotFoundError(profile_name=arguments.source_profile)
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
                    region=profile_lib.get_region(profiles, arguments, config),
                    mfa_serial=mfa_serial,
                    mfa_token=arguments.mfa_token,
                    ignore_cache=arguments.force_refresh,
                    duration_seconds=config.get('debug', {}).get('session_token_duration'),
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


def get_assume_role_credentials(config: dict, arguments: argparse.Namespace, profiles: dict, target_profile: dict, role_duration: int, source_credentials: dict, target_profile_name: str):
    logger.info('Getting assume role credentials')
    region = profile_lib.get_region(profiles, arguments, config)
    external_id = profile_lib.get_external_id(arguments, target_profile)
    if not source_credentials:
        source_profile = profile_lib.get_source_profile(profiles, target_profile_name)
        source_credentials = profile_lib.profile_to_credentials(source_profile)
    role_session = aws_lib.assume_role(
        source_credentials,
        target_profile.get('role_arn'),
        profile_lib.get_session_name(config, arguments, profiles, target_profile_name),
        region=region,
        external_id=external_id,
        role_duration=role_duration,
    )
    if 'SourceExpiration' in source_credentials:
        role_session['SourceExpiration'] = source_credentials['SourceExpiration']
    elif 'Expiration' in source_credentials:
        role_session['SourceExpiration'] = source_credentials['Expiration']
    return role_session


def get_assume_role_credentials_mfa_required(config: dict, arguments: argparse.Namespace, profiles: dict, target_profile: dict, role_duration: int, source_credentials: dict, target_profile_name: str):
    logger.info('Getting assume role credentials MFA required')
    region = profile_lib.get_region(profiles, arguments, config)
    mfa_serial = profile_lib.get_mfa_serial(profiles, target_profile_name)
    external_id = profile_lib.get_external_id(arguments, target_profile)
    source_profile = profile_lib.get_source_profile(profiles, target_profile_name)
    if source_profile:
        if 'role_arn' not in source_profile:
            logger.debug('Calling get_session_token to assume role with')
            if not source_credentials:
                source_credentials = profile_lib.profile_to_credentials(source_profile)
            source_session = aws_lib.get_session_token(
                source_credentials,
                region=region,
                mfa_serial=mfa_serial,
                mfa_token=arguments.mfa_token,
                ignore_cache=arguments.force_refresh,
                duration_seconds=config.get('debug', {}).get('session_token_duration'),
            )
        else:
            source_session = source_credentials
    elif 'credential_source' in target_profile and target_profile['credential_source'] in VALID_CREDENTIAL_SOURCES:
        logger.debug('Using current environment to assume role')
        source_session = {}

    if arguments.auto_refresh and (os.environ.get('AWS_PROFILE', '').startswith('autoawsume-') or profiles.get(os.getenv('AWS_PROFILE'), {}).get('autoawsume')):
        os.environ.pop('AWS_PROFILE')
        os.environ.pop('AWS_DEFAULT_PROFILE')

    role_session = aws_lib.assume_role(
        source_session,
        target_profile.get('role_arn'),
        profile_lib.get_session_name(config, arguments, profiles, target_profile_name),
        region=region,
        external_id=external_id,
        role_duration=role_duration,
    )

    if 'SourceExpiration' in source_session:
        role_session['SourceExpiration'] = source_session['SourceExpiration']
    elif 'Expiration' in source_session:
        role_session['SourceExpiration'] = source_session['Expiration']

    return source_session, role_session


def get_assume_role_credentials_mfa_required_large_custom_duration(config: dict, arguments: argparse.Namespace, profiles: dict, target_profile: dict, role_duration: int, target_profile_name: str):
    logger.info('Getting assume role credentials MFA required, large custom duration')
    if arguments.auto_refresh and role_duration > 3600:
        raise exceptions.ValidationException('Cannot use autoawsume with custom role duration of more than 1 hour')
    logger.debug('Skipping the get_session_token call, temp creds cannot be used for custom role duration')

    region = profile_lib.get_region(profiles, arguments, config)
    mfa_serial = profile_lib.get_mfa_serial(profiles, target_profile_name)
    external_id = profile_lib.get_external_id(arguments, target_profile)
    source_profile = profile_lib.get_source_profile(profiles, target_profile_name)
    source_session = profile_lib.profile_to_credentials(source_profile)

    role_session = aws_lib.assume_role(
        source_session,
        target_profile.get('role_arn'),
        profile_lib.get_session_name(config, arguments, profiles, target_profile_name),
        region=region,
        external_id=external_id,
        role_duration=role_duration,
        mfa_serial=mfa_serial,
        mfa_token=arguments.mfa_token,
    )
    return role_session


def get_credentials_no_mfa(config: dict, arguments: argparse.Namespace, profiles: dict, target_profile: dict):
    logger.info('Getting credentials MFA not required')
    region = profile_lib.get_region(profiles, arguments, config)
    return_session = profile_lib.profile_to_credentials(target_profile)
    return_session['Region'] = region
    return return_session


def get_credentials_from_credential_source(config: dict, arguments: argparse.Namespace, profiles: dict, target_profile: dict, target_profile_name: str):
    logger.info('Getting credentials from credential_source')
    region = profile_lib.get_region(profiles, arguments, config)
    return_session = {'AwsProfile': target_profile_name}
    return_session['Region'] = region
    return return_session


def get_credentials_from_credential_process(config: dict, arguments: argparse.Namespace, profiles: dict, target_profile: dict, target_profile_name: str):
    logger.info('Getting credentials from credential_process, profile: %s'% target_profile_name)
    region = profile_lib.get_region(profiles, arguments, config)
    return_session = {}
    result = subprocess.run(target_profile.get('credential_process').split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info('credential_process returncode: {}'.format(result.returncode))
    logger.debug('credential_process stdout: {}'.format(result.stdout.decode('utf-8')))
    logger.debug('credential_process stderr: {}'.format(result.stderr.decode('utf-8')))
    if result.returncode:
        logger.debug('No creds returned from credential_process: {}'.format(result))
        message = result.stderr.decode('utf-8') or result.stdout.decode('utf-8') or 'No output from the process'
        raise exceptions.NoCredentialsError('credential_process error: {}'.format(message))
    try:
        creds = json.loads(result.stdout.decode('utf-8'))
    except json.JSONDecodeError as err:
        raise exceptions.ValidationException('Invalid credentials returned from credential_process: {}'.format(err))
    logger.debug('Obtained creds: {}'.format(creds))
    if not creds:
        raise exceptions.NoCredentialsError('credential_process did not return a valid session')
    return_session = {}
    if 'AccessKeyId' in creds:
        return_session['AccessKeyId'] = creds['AccessKeyId']
    if 'SecretAccessKey' in creds:
        return_session['SecretAccessKey'] = creds['SecretAccessKey']
    if 'SessionToken' in creds:
        return_session['SessionToken'] = creds['SessionToken']
    if 'Expiration' in creds:
        return_session['Expiration'] = dateutil.parser.parse(creds['Expiration'])
    return_session['Region'] = region
    logger.debug("credential_process session: {}".format(return_session))
    return return_session


def get_session_token_credentials(config: dict, arguments: argparse.Namespace, profiles: dict, target_profile: dict, target_profile_name: str):
    logger.info('Getting session token credentials')
    region = profile_lib.get_region(profiles, arguments, config)
    mfa_serial = profile_lib.get_mfa_serial(profiles, target_profile_name)
    source_credentials = profile_lib.profile_to_credentials(target_profile)
    user_session = aws_lib.get_session_token(
        source_credentials,
        region=region,
        mfa_serial=mfa_serial,
        mfa_token=arguments.mfa_token,
        ignore_cache=arguments.force_refresh,
        duration_seconds=config.get('debug', {}).get('session_token_duration'),
    )
    return user_session


def get_credentials_handler(config: dict, arguments: argparse.Namespace, profiles: dict, profile_name: str, credentials: dict) -> dict:
    credentials = credentials if credentials else {}
    logger.info('Getting credentials: {}'.format(profile_name))

    user_session = None
    role_session = None

    if arguments.role_arn:
        role_session = assume_role_from_cli(config, arguments, profiles)
    else:
        profile_lib.validate_profile(config, arguments, profiles, profile_name)
        target_profile = profiles.get(profile_name)
        mfa_serial = profile_lib.get_mfa_serial(profiles, profile_name)
        role_duration = profile_lib.get_role_duration(config, arguments, target_profile)

        if 'credential_process' in target_profile:
            session = get_credentials_from_credential_process(config, arguments, profiles, target_profile, profile_name)
            if 'Expiration' in session:
                role_session = session
            else:
                user_session = session
        elif 'role_arn' in target_profile:
            logger.debug('assume_role call needed')
            if mfa_serial and not credentials: # if using specific credentials, no mfa needed
                if role_duration > 3600: # cannot use temp creds with custom role duration more than an hour
                    role_session = get_assume_role_credentials_mfa_required_large_custom_duration(config, arguments, profiles, target_profile, role_duration, profile_name)
                else:
                    user_session, role_session = get_assume_role_credentials_mfa_required(config, arguments, profiles, target_profile, role_duration, credentials, profile_name)
            else:
                role_session = get_assume_role_credentials(config, arguments, profiles, target_profile, role_duration, credentials, profile_name)
        else:
            if mfa_serial:
                user_session = get_session_token_credentials(config, arguments, profiles, target_profile, profile_name)
            elif 'credential_source' in target_profile:
                user_session = get_credentials_from_credential_source(config, arguments, profiles, target_profile, profile_name)
            else:
                user_session = get_credentials_no_mfa(config, arguments, profiles, target_profile)

    if config.get('is_interactive'):
        if user_session and user_session.get('Expiration'):
            safe_print('Session token will expire at {}'.format(profile_lib.parse_time(user_session['Expiration'])), colorama.Fore.GREEN)
        if role_session and role_session.get('Expiration'):
            safe_print('[{}] Role credentials will expire {}'.format(profile_name, profile_lib.parse_time(role_session['Expiration'])), colorama.Fore.GREEN)

    return role_session or user_session


@hookimpl(tryfirst=True)
def get_credentials(config: dict, arguments: argparse.Namespace, profiles: dict) -> dict:
    if arguments.role_arn:
        target_profile_name = arguments.role_arn
    else:
        target_profile_name = get_profile_name(config, profiles, arguments.target_profile_name)
    arguments.target_profile_name = target_profile_name
    role_chain = get_role_chain(config, arguments, profiles, target_profile_name)
    logger.debug('Role chain: {}'.format(role_chain))
    credentials = None
    for profile_name in role_chain:
        credentials = get_credentials_handler(config=config, arguments=arguments, profiles=profiles, profile_name=profile_name, credentials=credentials)
    return credentials
