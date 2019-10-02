import json
import subprocess
import configparser
import time
import sys
from datetime import datetime, timedelta
import dateutil

from ..awsumepy.lib.aws_files import get_aws_files, delete_section
from ..awsumepy.lib import exceptions
from .. import awsumepy


def main():
    _, credentials_file = get_aws_files(None, None)
    while True:
        credentials = configparser.ConfigParser()
        credentials.read(credentials_file)
        auto_profiles = {k: dict(v) for k, v in credentials._sections.items() if k.startswith('autoawsume-')}

        expirations = []
        for profile_name, auto_profile in auto_profiles.items():
            expiration = datetime.strptime(auto_profile['expiration'], '%Y-%m-%d %H:%M:%S')
            source_expiration = datetime.strptime(auto_profile['source_expiration'], '%Y-%m-%d %H:%M:%S')
            if source_expiration < datetime.now():
                if expiration < datetime.now():
                    delete_section(profile_name, credentials_file)
                else:
                    expirations.append(expiration)
            else:
                if expiration < datetime.now():
                    session = refresh_profile(auto_profile)
                    if session:
                        expirations.append(session.awsume_credentials.get('Expiration'))
                    else:
                        delete_section(profile_name, credentials_file)
                else:
                    expirations.append(expiration)
                    expirations.append(source_expiration)

        if not expirations:
            break

        local_expirations = [_.astimezone(dateutil.tz.tzlocal()) for _ in expirations]
        earliest_expiration = min(local_expirations)
        time_to_sleep = (earliest_expiration - datetime.now().replace(tzinfo=earliest_expiration.tzinfo)).total_seconds() + 60
        time.sleep(time_to_sleep)


def refresh_profile(auto_profile):
    try:
        session = awsumepy.awsume(*auto_profile.get('awsumepy_command').split(' '))
        return session
    except exceptions.AwsumeException:
        return None
