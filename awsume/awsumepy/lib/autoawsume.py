import argparse

from . import aws_files as aws_files_lib
from . import profile as profile_lib


def create_autoawsume_profile(config: dict, arguments: argparse.Namespace, role_session: dict, source_session: dict):
    _, credentials_file = aws_files_lib.get_aws_files(arguments, config)
    autoawsume_profile_name = 'autoawsume-{}'.format(arguments.target_profile_name)
    profile = profile_lib.credentials_to_profile(role_session)
    profile['expiration'] = role_session.get('Expiration').strftime('%Y-%m-%d %H:%M:%S')
    profile['source_expiration'] = source_session.get('Expiration').strftime('%Y-%m-%d %H:%M:%S')
    profile['awsumepy_command'] = ' '.join(arguments.system_arguments)
    aws_files_lib.add_section(autoawsume_profile_name, profile, credentials_file, True)
