from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch
import dateutil
import pytest
from awsume.awsumepy.lib import aws, constants
from awsume.awsumepy.lib.exceptions import RoleAuthenticationError, UserAuthenticationError


def test_parse_time():
    now = datetime.now()
    result = aws.parse_time(now)
    assert result == now.astimezone(dateutil.tz.tzlocal()).strftime('%Y-%m-%d %H:%M:%S')


@patch.object(aws, 'safe_print')
@patch('boto3.session.Session')
def test_assume_role(Session: MagicMock, safe_print: MagicMock):
    expiration = MagicMock()
    source_credentials = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKeyId': 'SECRET',
        'SessionToken': 'LONG',
    }
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    Session.return_value = session
    client.assume_role.return_value = {
        'Credentials': {
            'AccessKeyId': 'AKIA...',
            'SecretAccessKeyId': 'SECRET',
            'SessionToken': 'LONG',
            'Expiration': expiration,
        },
    }

    result = aws.assume_role(
        source_credentials, 'myrolearn', 'mysessionname',
        external_id='myexternalid',
        region='us-east-2',
        role_duration=1234,
        mfa_serial='mymfaserial',
        mfa_token='123123',
    )

    Session.assert_called_with(
        aws_access_key_id=source_credentials.get('AccessKeyId'),
        aws_secret_access_key=source_credentials.get('SecretAccessKey'),
        aws_session_token=source_credentials.get('SessionToken'),
        region_name='us-east-2',
    )
    client.assume_role.assert_called_with(
        RoleSessionName='mysessionname',
        RoleArn='myrolearn',
        ExternalId='myexternalid',
        DurationSeconds=1234,
        SerialNumber='mymfaserial',
        TokenCode='123123',
    )
    result.get('Expiration').astimezone.assert_called_with(dateutil.tz.tzlocal())


@patch.object(aws, 'safe_print')
@patch('boto3.session.Session')
def test_assume_role_minimal_parameters(Session: MagicMock, safe_print: MagicMock):
    expiration = MagicMock()
    source_credentials = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKeyId': 'SECRET',
        'SessionToken': 'LONG',
    }
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    Session.return_value = session
    client.assume_role.return_value = {
        'Credentials': {
            'AccessKeyId': 'AKIA...',
            'SecretAccessKeyId': 'SECRET',
            'SessionToken': 'LONG',
            'Expiration': expiration,
        },
    }

    result = aws.assume_role(
        source_credentials, 'myrolearn', 'mysessionname',
    )

    Session.assert_called_with(
        aws_access_key_id=source_credentials.get('AccessKeyId'),
        aws_secret_access_key=source_credentials.get('SecretAccessKey'),
        aws_session_token=source_credentials.get('SessionToken'),
        region_name='us-east-1',
    )
    client.assume_role.assert_called_with(
        RoleSessionName='mysessionname',
        RoleArn='myrolearn',
    )
    result.get('Expiration').astimezone.assert_called_with(dateutil.tz.tzlocal())



@patch.object(aws, 'safe_print')
@patch('boto3.session.Session')
def test_assume_role_raise_exception(Session: MagicMock, safe_print: MagicMock):
    source_credentials = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKeyId': 'SECRET',
        'SessionToken': 'LONG',
    }
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    Session.return_value = session
    client.assume_role.side_effect = Exception('Some Error')

    with pytest.raises(RoleAuthenticationError):
        aws.assume_role(source_credentials, 'myrolearn', 'mysessionname')


@patch('awsume.awsumepy.lib.cache.write_aws_cache')
@patch('awsume.awsumepy.lib.cache.valid_cache_session')
@patch('awsume.awsumepy.lib.cache.read_aws_cache')
@patch.object(aws, 'safe_print')
@patch('boto3.session.Session')
def test_get_session_token(Session: MagicMock, safe_print: MagicMock, read_aws_cache: MagicMock, valid_cache_session: MagicMock, write_aws_cache: MagicMock):
    expiration = MagicMock()
    source_credentials = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKeyId': 'SECRET',
        'SessionToken': 'LONG',
    }
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    Session.return_value = session
    client.get_session_token.return_value = {
        'Credentials': {
            'AccessKeyId': 'AKIA...',
            'SecretAccessKeyId': 'SECRET',
            'SessionToken': 'LONG',
            'Expiration': expiration,
        },
    }
    read_aws_cache.return_value = {}
    valid_cache_session.return_value = False

    result = aws.get_session_token(
        source_credentials,
        region='us-east-2',
        mfa_serial='mymfaserial',
        mfa_token='123123',
        ignore_cache=False,
    )

    Session.assert_called_with(
        aws_access_key_id=source_credentials.get('AccessKeyId'),
        aws_secret_access_key=source_credentials.get('SecretAccessKey'),
        aws_session_token=source_credentials.get('SessionToken'),
        region_name='us-east-2',
    )
    client.get_session_token.assert_called_with(
        SerialNumber='mymfaserial',
        TokenCode='123123',
    )
    result.get('Expiration').astimezone.assert_called_with(dateutil.tz.tzlocal())
    write_aws_cache.assert_called()


@patch('awsume.awsumepy.lib.cache.write_aws_cache')
@patch('awsume.awsumepy.lib.cache.valid_cache_session')
@patch('awsume.awsumepy.lib.cache.read_aws_cache')
@patch.object(aws, 'safe_print')
@patch('boto3.session.Session')
def test_get_session_token_valid_cache(Session: MagicMock, safe_print: MagicMock, read_aws_cache: MagicMock, valid_cache_session: MagicMock, write_aws_cache: MagicMock):
    expiration = MagicMock()
    source_credentials = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKeyId': 'SECRET',
        'SessionToken': 'LONG',
    }
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    Session.return_value = session
    client.get_session_token.return_value = {
        'Credentials': {
            'AccessKeyId': 'AKIA...',
            'SecretAccessKeyId': 'SECRET',
            'SessionToken': 'LONG',
            'Expiration': expiration,
        },
    }
    read_aws_cache.return_value = {'Expiration': datetime.now()}
    valid_cache_session.return_value = True
    write_aws_cache = MagicMock()

    result = aws.get_session_token(
        source_credentials,
        region='us-east-2',
        mfa_serial='mymfaserial',
        mfa_token='123123',
        ignore_cache=False,
    )

    Session.assert_not_called()
    client.get_session_token.assert_not_called()
    assert result == read_aws_cache.return_value


@patch('awsume.awsumepy.lib.cache.write_aws_cache')
@patch('awsume.awsumepy.lib.cache.valid_cache_session')
@patch('awsume.awsumepy.lib.cache.read_aws_cache')
@patch.object(aws, 'safe_print')
@patch('boto3.session.Session')
def test_get_session_token_ignore_cache(Session: MagicMock, safe_print: MagicMock, read_aws_cache: MagicMock, valid_cache_session: MagicMock, write_aws_cache: MagicMock):
    expiration = MagicMock()
    source_credentials = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKeyId': 'SECRET',
        'SessionToken': 'LONG',
    }
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    Session.return_value = session
    client.get_session_token.return_value = {
        'Credentials': {
            'AccessKeyId': 'AKIA...',
            'SecretAccessKeyId': 'SECRET',
            'SessionToken': 'LONG',
            'Expiration': expiration,
        },
    }
    read_aws_cache.return_value = {}
    valid_cache_session.return_value = True

    result = aws.get_session_token(
        source_credentials,
        region='us-east-2',
        mfa_serial='mymfaserial',
        mfa_token='123123',
        ignore_cache=True,
    )

    Session.assert_called_with(
        aws_access_key_id=source_credentials.get('AccessKeyId'),
        aws_secret_access_key=source_credentials.get('SecretAccessKey'),
        aws_session_token=source_credentials.get('SessionToken'),
        region_name='us-east-2',
    )
    client.get_session_token.assert_called_with(
        SerialNumber='mymfaserial',
        TokenCode='123123',
    )
    result.get('Expiration').astimezone.assert_called_with(dateutil.tz.tzlocal())
    write_aws_cache.assert_called()


@patch('awsume.awsumepy.lib.cache.write_aws_cache')
@patch('awsume.awsumepy.lib.cache.valid_cache_session')
@patch('awsume.awsumepy.lib.cache.read_aws_cache')
@patch.object(aws, 'safe_print')
@patch('boto3.session.Session')
def test_get_session_token_ignore_cache(Session: MagicMock, safe_print: MagicMock, read_aws_cache: MagicMock, valid_cache_session: MagicMock, write_aws_cache: MagicMock):
    expiration = MagicMock()
    source_credentials = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKeyId': 'SECRET',
        'SessionToken': 'LONG',
    }
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    Session.return_value = session
    client.get_session_token.side_effect = Exception('SomeException')
    read_aws_cache.return_value = {}
    valid_cache_session.return_value = False

    with pytest.raises(UserAuthenticationError):
        aws.get_session_token(source_credentials)


@patch('boto3.session.Session')
def test_get_account_id(Session: MagicMock):
    source_credentials = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKeyId': 'SECRET',
        'SessionToken': 'LONG',
    }
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    Session.return_value = session
    client.get_caller_identity.return_value = {'Account': '123123123123'}

    result = aws.get_account_id(source_credentials)

    Session.assert_called_with(
        aws_access_key_id=source_credentials.get('AccessKeyId'),
        aws_secret_access_key=source_credentials.get('SecretAccessKey'),
        aws_session_token=source_credentials.get('SessionToken'),
        region_name='us-east-1',
    )
    assert result == '123123123123'


@patch('boto3.session.Session')
def test_get_account_id_raise_exception(Session: MagicMock):
    source_credentials = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKeyId': 'SECRET',
        'SessionToken': 'LONG',
    }
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    Session.return_value = session
    client.get_caller_identity.side_effect = Exception('Some error')

    result = aws.get_account_id(source_credentials)

    Session.assert_called_with(
        aws_access_key_id=source_credentials.get('AccessKeyId'),
        aws_secret_access_key=source_credentials.get('SecretAccessKey'),
        aws_session_token=source_credentials.get('SessionToken'),
        region_name='us-east-1',
    )
    assert result == 'Unavailable'
