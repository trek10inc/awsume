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
    role_session = {'Expiration': now}
    source_session = {'Expiration': now}
    args = argparse.Namespace(target_profile_name='profile', system_arguments=['awsumepy', 'profile'])

    autoawsume.create_autoawsume_profile(config, args, role_session, source_session)

    aws_files.add_section.assert_called_with('autoawsume-profile', {
        'aws_access_key_id': 'AKIA...',
        'aws_secret_access_key': 'SECRET',
        'aws_session_token': 'LONG',
        'expiration': now_str,
        'source_expiration': now_str,
        'awsumepy_command': 'awsumepy profile',
    }, 'credentials/file', True)
