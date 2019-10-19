import argparse
import dateutil
import boto3
import colorama
from datetime import datetime

from . import profile as profile_lib
from . import cache as cache_lib
from . exceptions import RoleAuthenticationError, UserAuthenticationError
from . logger import logger
from . safe_print import safe_print


DEFAULT_REGION = 'us-east-1'


def assume_role(
    source_credentials: dict,
    role_arn: str,
    session_name: str,
    external_id: str = None,
    region: str = None,
    role_duration: int = None,
    mfa_serial: str = None,
    mfa_token: str = None,
) -> dict:
    if len(session_name) < 2:
        session_name = session_name.center(2, '_')

    logger.debug('Assuming role: {}'.format(role_arn))
    logger.debug('Session name: {}'.format(session_name))
    try:
        boto_session = boto3.session.Session(
            aws_access_key_id=source_credentials.get('AccessKeyId'),
            aws_secret_access_key=source_credentials.get('SecretAccessKey'),
            aws_session_token=source_credentials.get('SessionToken'),
            region_name=region,
        )
        role_sts_client = boto_session.client('sts') # type: botostubs.STS
        kwargs = { 'RoleSessionName': session_name, 'RoleArn': role_arn }
        if external_id:
            kwargs['ExternalId'] = external_id
        if role_duration:
            kwargs['DurationSeconds'] = int(role_duration)
        if mfa_serial:
            kwargs['SerialNumber'] = mfa_serial
            kwargs['TokenCode'] = mfa_token or profile_lib.get_mfa_token()
        logger.debug('Assuming role now')
        role_session = role_sts_client.assume_role(**kwargs).get('Credentials')
        logger.debug('Received role credentials')
        role_session['Expiration'] = role_session['Expiration'].astimezone(dateutil.tz.tzlocal())
        role_session['Region'] = region or boto_session.region_name
    except Exception as e:
        raise RoleAuthenticationError(str(e))
    logger.debug('Role credentials received')
    return role_session


def get_session_token(
    source_credentials: dict,
    region: str = None,
    mfa_serial: str = None,
    mfa_token: str = None,
    ignore_cache: bool = False,
    duration_seconds: int = None,
) -> dict:
    cache_file_name = 'aws-credentials-' + source_credentials.get('AccessKeyId')
    cache_session = cache_lib.read_aws_cache(cache_file_name)

    if cache_lib.valid_cache_session(cache_session) and not ignore_cache:
        logger.debug('Using cache session')
        if region:
            cache_session['Region'] = region
        user_session = cache_session
    else:
        logger.debug('Getting session token')
        boto_session = boto3.session.Session(
            aws_access_key_id=source_credentials.get('AccessKeyId'),
            aws_secret_access_key=source_credentials.get('SecretAccessKey'),
            aws_session_token=source_credentials.get('SessionToken'),
            region_name=region,
        )
        user_sts_client = boto_session.client('sts') # type: botostubs.STS
        try:
            kwargs = {
                'SerialNumber': mfa_serial if mfa_serial else None,
                'TokenCode': None if not mfa_serial else (mfa_token or profile_lib.get_mfa_token()),
            }
            if duration_seconds:
                kwargs['DurationSeconds'] = duration_seconds
            user_session = user_sts_client.get_session_token(**kwargs).get('Credentials')
            user_session['Expiration'] = user_session['Expiration'].astimezone(dateutil.tz.tzlocal())
            user_session['Region'] = region or boto_session.region_name
        except Exception as e:
            raise UserAuthenticationError(str(e))
        logger.debug('Session token received')
        cache_lib.write_aws_cache(cache_file_name, user_session)
    return user_session


def get_account_id(credentials: dict):
    try:
        sts_client = boto3.session.Session(
            aws_access_key_id=credentials.get('AccessKeyId'),
            aws_secret_access_key=credentials.get('SecretAccessKey'),
            aws_session_token=credentials.get('SessionToken'),
            region_name=credentials.get('Region', 'us-east-1'),
        ).client('sts') # type: botostubs.STS
        response = sts_client.get_caller_identity()
        return response.get('Account', 'Unavailable')
    except:
        return 'Unavailable'


def assume_role_with_saml(
    role_arn: str,
    principal_arn: str,
    saml_assertion: str,
    region: str = 'us-east-1',
    role_duration: int = None,
) -> dict:
    logger.debug('Assuming role with saml: {}'.format(role_arn))
    role_sts_client = boto3.session.Session().client('sts') # type: botostubs.STS

    try:
        kwargs = { 'RoleArn': role_arn, 'PrincipalArn': principal_arn, 'SAMLAssertion': saml_assertion }
        if role_duration:
            kwargs['DurationSeconds'] = int(role_duration)
        role_session = role_sts_client.assume_role_with_saml(**kwargs).get('Credentials')
        role_session['Expiration'] = role_session['Expiration'].astimezone(dateutil.tz.tzlocal())
        role_session['Region'] = region
    except Exception as e:
        raise RoleAuthenticationError(str(e))
    logger.debug('Role credentials received')
    safe_print('Role credentials will expire {}'.format(profile_lib.parse_time(role_session['Expiration'])), colorama.Fore.GREEN)
    return role_session
