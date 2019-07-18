import json
import subprocess
import configparser
import time
from datetime import datetime, timedelta

from ..awsumepy.lib.aws_files import get_aws_files, delete_section


def main():
    _, credentials_file = get_aws_files(None, None)
    while True:
        credentials = configparser.ConfigParser()
        credentials.read(credentials_file)
        auto_profiles = {k: dict(v) for k, v in credentials._sections.items() if k.startswith('autoawsume-')}

        expirations = []
        for _, auto_profile in auto_profiles.items():
            expiration = datetime.strptime(auto_profile['expiration'], '%Y-%m-%d %H:%M:%S')
            source_expiration = datetime.strptime(auto_profile['source_expiration'], '%Y-%m-%d %H:%M:%S')

            if source_expiration < datetime.now() + timedelta(minutes=5):
                continue

            if expiration < datetime.now() + timedelta(minutes=5):
                subprocess.run(auto_profile.get('awsumepy_command').split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                expirations.append(datetime.now() + timedelta(hours=1))
            else:
                expirations.append(expiration)

        if not expirations:
            break

        earliest_expiration = min(expirations)
        time_to_sleep = (earliest_expiration - datetime.now().replace(tzinfo=earliest_expiration.tzinfo)).total_seconds()
        time.sleep(time_to_sleep)
