import argparse
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch
from awsume.awsumepy.lib import autoawsume


@patch.object(autoawsume, 'aws_files_lib')
@patch.object(autoawsume, 'profile_lib')
def test_create_autoawsume_profile(profile: MagicMock, aws_files: MagicMock):
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    aws_files.get_aws_files.return_value = 'config/file', 'credentials/file'
    profile.credentials_to_profile.return_value = {
        'aws_access_key_id': 'AKIA...',
        'aws_secret_access_key': 'SECRET',
        'aws_session_token': 'LONG',
    }
    config = {}
    profiles = {}
    role_session = {'Expiration': now, 'SourceExpiration': now}
    args = argparse.Namespace(target_profile_name='profile', system_arguments=['awsumepy', 'profile'], output_profile=None)

    autoawsume.create_autoawsume_profile(config, args, profiles, role_session)

    aws_files.add_section.assert_called_with('autoawsume-profile', {
        'aws_access_key_id': 'AKIA...',
        'aws_secret_access_key': 'SECRET',
        'aws_session_token': 'LONG',
        'autoawsume': 'true',
        'expiration': now_str,
        'source_expiration': now_str,
        'awsumepy_command': 'awsumepy profile',
    }, 'credentials/file', True)


@patch.object(autoawsume, 'aws_files_lib')
@patch.object(autoawsume, 'profile_lib')
def test_create_autoawsume_profile_no_expiration(profile: MagicMock, aws_files: MagicMock):
    aws_files.get_aws_files.return_value = 'config/file', 'credentials/file'
    profile.credentials_to_profile.return_value = {
        'aws_access_key_id': 'AKIA...',
        'aws_secret_access_key': 'SECRET',
        'aws_session_token': 'LONG',
    }
    config = {}
    profiles = {}
    role_session = {}
    args = argparse.Namespace(target_profile_name='profile', system_arguments=['awsumepy', 'profile'], output_profile=None)

    autoawsume.create_autoawsume_profile(config, args, profiles, role_session)

    aws_files.add_section.assert_called_with('autoawsume-profile', {
        'aws_access_key_id': 'AKIA...',
        'aws_secret_access_key': 'SECRET',
        'aws_session_token': 'LONG',
        'autoawsume': 'true',
        'awsumepy_command': 'awsumepy profile',
    }, 'credentials/file', True)
