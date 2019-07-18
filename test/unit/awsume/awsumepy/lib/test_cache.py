import os
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from awsume.awsumepy.lib import cache


@patch('os.makedirs')
@patch('os.path.exists')
def test_ensure_cache_dir(exists: MagicMock, makedirs: MagicMock):
    exists.return_value = False

    cache.ensure_cache_dir()

    makedirs.assert_called()


@patch('os.makedirs')
@patch('os.path.exists')
def test_ensure_cache_dir_already_exists(exists: MagicMock, makedirs: MagicMock):
    exists.return_value = True

    cache.ensure_cache_dir()

    makedirs.assert_not_called()



@patch('builtins.open')
@patch('json.load')
@patch('os.path.isfile')
@patch.object(cache, 'ensure_cache_dir')
def test_read_aws_cache(ensure_cache_dir: MagicMock, is_file: MagicMock, json_load: MagicMock, open: MagicMock):
    is_file.return_value = True
    json_load.return_value = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
        'Expiration': '2065-10-24 12:24:36',
    }

    result = cache.read_aws_cache('cache-file')

    ensure_cache_dir.assert_called()
    open.assert_called()
    json_load.assert_called()
    assert type(result.get('Expiration')) is datetime



@patch('builtins.open')
@patch('json.load')
@patch('os.path.isfile')
@patch.object(cache, 'ensure_cache_dir')
def test_read_aws_cache_no_expiration(ensure_cache_dir: MagicMock, is_file: MagicMock, json_load: MagicMock, open: MagicMock):
    is_file.return_value = True
    json_load.return_value = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
    }

    result = cache.read_aws_cache('cache-file')

    ensure_cache_dir.assert_called()
    open.assert_called()
    json_load.assert_called()
    assert result == json_load.return_value



@patch('builtins.open')
@patch('json.load')
@patch('os.path.isfile')
@patch.object(cache, 'ensure_cache_dir')
def test_read_aws_cache_no_file(ensure_cache_dir: MagicMock, is_file: MagicMock, json_load: MagicMock, open: MagicMock):
    is_file.return_value = False

    result = cache.read_aws_cache('cache-file')

    ensure_cache_dir.assert_called()
    assert result == {}



@patch('builtins.open')
@patch('json.load')
@patch('os.path.isfile')
@patch.object(cache, 'ensure_cache_dir')
def test_read_aws_cache_catch_exception(ensure_cache_dir: MagicMock, is_file: MagicMock, json_load: MagicMock, open: MagicMock):
    is_file.return_value = True
    json_load.side_effect = Exception('Some exception')

    cache.read_aws_cache('cache-file')



@patch('builtins.open')
@patch('json.dump')
@patch('os.path.isfile')
@patch.object(cache, 'ensure_cache_dir')
def test_write_aws_cache(ensure_cache_dir: MagicMock, is_file: MagicMock, json_dump: MagicMock, open: MagicMock):
    is_file.return_value = True
    session = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
        'Expiration': datetime.now(),
    }
    cache.write_aws_cache('cache-file', session)

    ensure_cache_dir.assert_called()
    open.assert_called()
    json_dump.assert_called()
    written_session = json_dump.call_args[0][0]
    assert type(written_session.get('Expiration')) is str



@patch('builtins.open')
@patch('json.dump')
@patch('os.path.isfile')
@patch.object(cache, 'ensure_cache_dir')
def test_write_aws_cache_catch_exception(ensure_cache_dir: MagicMock, is_file: MagicMock, json_dump: MagicMock, open: MagicMock):
    is_file.return_value = True
    json_dump.side_effect = Exception('Some Exception')
    session = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
        'Expiration': datetime.now(),
    }
    cache.write_aws_cache('cache-file', session)



def test_valid_cache_session():
    result = cache.valid_cache_session({
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
        'Expiration': datetime.now() + timedelta(hours=1),
    })
    assert result is True



def test_valid_cache_session_expired():
    result = cache.valid_cache_session({
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
        'Expiration': datetime.now() - timedelta(hours=1),
    })
    assert result is False



def test_valid_cache_session_no_access_key_id():
    result = cache.valid_cache_session({
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
        'Expiration': datetime.now() + timedelta(hours=1),
    })
    assert result is False



def test_valid_cache_session_no_secret_access_key():
    result = cache.valid_cache_session({
        'AccessKeyId': 'AKIA...',
        'SessionToken': 'LONGSECRET',
        'Expiration': datetime.now() + timedelta(hours=1),
    })
    assert result is False



def test_valid_cache_session_no_session_token():
    result = cache.valid_cache_session({
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'Expiration': datetime.now() + timedelta(hours=1),
    })
    assert result is False



def test_valid_cache_session_no_expiration():
    result = cache.valid_cache_session({
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
    })
    assert result is True



def test_valid_cache_session_datetime_str():
    result = cache.valid_cache_session({
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
        'Expiration': '2065-10-24 12:24:36',
    })
    assert result is True
