import argparse
import psutil

from ..awsumepy.lib.aws_files import delete_section, get_aws_files, read_aws_file
from ..awsumepy.lib.logger import logger


def kill_autoawsume():
    logger.debug('Killing autoawsume')
    for proc in psutil.process_iter():
        try:
            for command_string in proc.cmdline():
                if 'autoawsume' in command_string:
                    proc.kill()
        except Exception:
            pass


def kill(arguments: argparse.Namespace):
    _, credentials_file = get_aws_files(None, None)
    if arguments.profile_name:
        logger.debug('Stoping auto-refresh of profile {}'.format(arguments.profile_name))
        profiles = read_aws_file(credentials_file)
        if 'autoawsume-{}'.format(arguments.profile_name) in profiles:
            delete_section('autoawsume-{}'.format(arguments.profile_name), credentials_file)
            profiles.pop('autoawsume-{}'.format(arguments.profile_name))
        if arguments.profile_name in profiles and profiles[arguments.profile_name].get('autoawsume'):
            delete_section(arguments.profile_name, credentials_file)
            profiles.pop(arguments.profile_name)
        autoawsume_profiles = [{k: v} for k, v in profiles.items() if v.get('autoawsume')]
        if any(autoawsume_profiles):
            print('Stop {}'.format(arguments.profile_name))
            return
        else:
            logger.debug('There were not more autoawsume profiles, stopping autoawsume')
            print('Kill')
            kill_autoawsume()
    else:
        logger.debug('Stopping all auto refreshing and removing autoawsume profiles')
        kill_autoawsume()
        profiles = read_aws_file(credentials_file)
        for profile in profiles:
            if 'autoawsume-' in profile or profiles[profile].get('autoawsume'):
                delete_section(profile, credentials_file)
        print('Kill')
