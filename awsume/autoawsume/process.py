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
        delete_section('autoawsume-{}'.format(arguments.profile_name), credentials_file)
        profiles = read_aws_file(credentials_file)
        profile_names = [_ for _ in profiles]
        if any(['autoawsume-' in _ for _ in profile_names]):
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
            if 'autoawsume-' in profile:
                delete_section(profile, credentials_file)
        print('Kill')
