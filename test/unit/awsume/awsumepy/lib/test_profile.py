import argparse
import pytest
from unittest.mock import patch, MagicMock

from awsume.awsumepy.lib.exceptions import ProfileNotFoundError, InvalidProfileError, UserAuthenticationError, RoleAuthenticationError
from awsume.awsumepy.lib import profile


def test_is_role():
    assert profile.is_role({}) is False
    assert profile.is_role({'role_arn': 'arn:aws:iam:XXX:role/role_name'}) is True


def test_profile_to_credentials():
    assert profile.profile_to_credentials({
        'aws_access_key_id': 'AKIA...',
        'aws_secret_access_key': 'SECRET',
        'aws_session_token': 'LONGSECRET',
        'region': 'us-east-1',
    }) == {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
        'Region': 'us-east-1',
    }


def test_credentials_to_profile():
    assert profile.credentials_to_profile({
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': 'LONGSECRET',
        'Region': 'us-east-1',
    }) == {
        'aws_access_key_id': 'AKIA...',
        'aws_secret_access_key': 'SECRET',
        'aws_session_token': 'LONGSECRET',
        'region': 'us-east-1',
    }


def test_credentials_to_profile_missing_keys():
    assert profile.credentials_to_profile({}) == {}


def test_validate_profile():
    profiles = {
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'source_profile': 'myuser',
        },
    }
    profile.validate_profile(profiles, 'myrole')


def test_validate_profile_no_profile():
    profiles = {
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'source_profile': 'myuser',
        },
    }
    with pytest.raises(ProfileNotFoundError):
        profile.validate_profile(profiles, 'admin')


def test_validate_profile_no_source_profile():
    profiles = {
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'source_profile': 'admin',
        },
    }
    with pytest.raises(ProfileNotFoundError):
        profile.validate_profile(profiles, 'myrole')


def test_validate_profile_no_source_profile_default():
    profiles = {
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
        },
    }
    with pytest.raises(ProfileNotFoundError):
        profile.validate_profile(profiles, 'myrole')


def test_validate_profile_user():
    profiles = {
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'source_profile': 'admin',
        },
    }
    profile.validate_profile(profiles, 'myuser')


def test_validate_profile_user_missing_access_key_id():
    profiles = {
        'myuser': {
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'source_profile': 'admin',
        },
    }
    with pytest.raises(InvalidProfileError):
        profile.validate_profile(profiles, 'myuser')


def test_validate_profile_user_missing_secret_access_key():
    profiles = {
        'myuser': {
            'aws_access_key_id': 'AKIA...',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'source_profile': 'admin',
        },
    }
    with pytest.raises(InvalidProfileError):
        profile.validate_profile(profiles, 'myuser')


def test_get_source_profile():
    profiles = {
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'source_profile': 'myuser',
        },
    }
    assert profile.get_source_profile(profiles, 'myrole') == profiles['myuser']


def test_get_source_profile_no_target_profile_name():
    profiles = {
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'source_profile': 'myuser',
        },
    }
    assert profile.get_source_profile(profiles, 'admin') == None


def test_get_source_profile_return_default():
    profiles = {
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
        },
    }
    assert profile.get_source_profile(profiles, 'myrole') == profiles['default']


def test_get_region():
    profiles = {
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'region': 'default-region',
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'region': 'myuser-region',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'region': 'myrole-region',
        },
    }
    assert profile.get_region(profiles, argparse.Namespace(region=None, role_arn=None, source_profile=None, target_profile_name='myrole')) == profiles['myrole']['region']


def test_get_region_arguments():
    profiles = {
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'region': 'default-region',
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'region': 'myuser-region',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'region': 'myrole-region',
        },
    }
    assert profile.get_region(profiles, argparse.Namespace(region='arguments-region', role_arn=None, source_profile=None, target_profile_name='myrole')) == 'arguments-region'


def test_get_region_cli_role_arn_and_source_profile():
    profiles = {
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'region': 'default-region',
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'region': 'myuser-region',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'region': 'myrole-region',
        },
    }
    assert profile.get_region(profiles, argparse.Namespace(region=None, role_arn='role-arn', source_profile='myuser', target_profile_name=None)) == profiles['myuser']['region']


def test_get_region_default_region():
    profiles = {
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'region': 'default-region'
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
        },
    }
    assert profile.get_region(profiles, argparse.Namespace(region=None, role_arn=None, source_profile=None, target_profile_name='myrole')) == profiles['default']['region']


def test_get_region_no_region():
    profiles = {
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
        },
    }
    assert profile.get_region(profiles, argparse.Namespace(region=None, role_arn=None, source_profile=None, target_profile_name='myrole')) == None


def test_get_mfa_serial():
    profiles = {
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'mfa_serial': 'role-mfa-serial',
        },
    }
    assert profile.get_mfa_serial(profiles, 'myrole') == 'role-mfa-serial'


def test_get_mfa_serial_from_source_profile():
    profiles = {
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'mfa_serial': 'source-mfa-serial',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
            'source_profile': 'myuser',
        },
    }
    assert profile.get_mfa_serial(profiles, 'myrole') == 'source-mfa-serial'


def test_get_mfa_serial_none():
    profiles = {
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
        },
    }
    assert profile.get_mfa_serial(profiles, 'myrole') == None


@patch('builtins.input')
@patch.object(profile, 'safe_print')
def test_get_mfa_token(safe_print: MagicMock, input: MagicMock):
    input.side_effect = ['123123']
    assert profile.get_mfa_token() == '123123'


@patch('builtins.input')
@patch.object(profile, 'safe_print')
def test_get_mfa_token_invalid_reprompt(safe_print: MagicMock, input: MagicMock):
    input.side_effect = ['1', '2', '123123']
    assert profile.get_mfa_token() == '123123'
    assert input.call_count == 3


def test_aggregate_profiles():
    result = [{
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }, {
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
        },
    }]
    assert profile.aggregate_profiles(result) == {
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
        },
    }


def test_aggregate_profiles_update_existing():
    result = [{
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }, {
        'default': {
            'region': 'us-east-1',
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
        },
    }]
    assert profile.aggregate_profiles(result) == {
        'default': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'region': 'us-east-1',
        },
        'myuser': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
        'myrole': {
            'role_arn': 'arn:aws:iam:XXX:role/role_name',
        },
    }


@patch('awsume.awsumepy.lib.aws.get_account_id')
def test_get_account_id_role_arn(get_account_id: MagicMock):
    assert profile.get_account_id({
        'role_arn': 'arn:aws:iam::123456789012:role/S3Access'
    }, False) == '123456789012'
    get_account_id.assert_not_called()


@patch('awsume.awsumepy.lib.aws.get_account_id')
def test_get_account_id_mfa_serial(get_account_id: MagicMock):
    assert profile.get_account_id({
        'mfa_serial': 'arn:aws:iam::123456789012:mfa/Bob'
    }, False) == '123456789012'
    get_account_id.assert_not_called()


@patch('awsume.awsumepy.lib.aws.get_account_id')
def test_get_account_id_unavailable(get_account_id: MagicMock):
    assert profile.get_account_id({}, False) == 'Unavailable'
    get_account_id.assert_not_called()


@patch('awsume.awsumepy.lib.aws.get_account_id')
def test_get_account_id_call_aws(get_account_id: MagicMock):
    get_account_id.return_value = '123987123987'
    assert profile.get_account_id({
        'aws_access_key_id': 'AKIA',
        'aws_secret_access_key': 'SECRET',
    }, True) == '123987123987'
