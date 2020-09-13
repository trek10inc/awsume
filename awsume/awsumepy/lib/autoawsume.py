import argparse

from . import aws_files as aws_files_lib
from . import profile as profile_lib
from . import safe_print
from . logger import logger
from . import exceptions


def create_autoawsume_profile(config: dict, arguments: argparse.Namespace, profiles: dict, role_session: dict):
    logger.info('Creating autoawsume profile')
    _, credentials_file = aws_files_lib.get_aws_files(arguments, config)
    autoawsume_profile_name = arguments.output_profile or 'autoawsume-{}'.format(arguments.target_profile_name)
    if not profile_lib.is_mutable_profile(profiles, autoawsume_profile_name):
        raise exceptions.ImmutableProfileError(autoawsume_profile_name, 'not awsume-managed')
    profile = profile_lib.credentials_to_profile(role_session)
    profile['autoawsume'] = 'true'
    profile['expiration'] = role_session.get('Expiration').strftime('%Y-%m-%d %H:%M:%S')
    if 'SourceExpiration' in role_session:
        profile['source_expiration'] = role_session.get('SourceExpiration').strftime('%Y-%m-%d %H:%M:%S')
    profile['awsumepy_command'] = ' '.join(arguments.system_arguments)
    aws_files_lib.add_section(autoawsume_profile_name, profile, credentials_file, True)
