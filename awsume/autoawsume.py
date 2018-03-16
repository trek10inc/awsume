"""autoawsume - A daemon to auto refresh 'auto-refresh' profiles in the credentials file"""
from __future__ import print_function
import sys
import datetime
import time
import botocore
import dateutil

from awsume import awsumepy
from awsume.awsumepy import AWS_CACHE_DIRECTORY, AWS_CREDENTIALS_FILE

def get_now(): # pragma: no cover
    """Return datetime.datetime.now()."""
    return datetime.datetime.now()

def refresh_session(autoProfile):
    """Refresh the `oldSession` role credentials.

    Parameters
    ----------
    - oldSession - the session to refresh;
    - roleArn - the role_arn used to make the assume_role call;
    - sessionName - what to name the assumed role session;

    Returns
    -------
    The refreshed role session
    """
    sourceCredentials = awsumepy.read_aws_cache(AWS_CACHE_DIRECTORY, autoProfile['awsume_cache_name'])
    stsClient = awsumepy.create_sts_client(sourceCredentials['AccessKeyId'],
                                           sourceCredentials['SecretAccessKey'],
                                           sourceCredentials['SessionToken'])
    try:
        response = stsClient.assume_role(RoleArn=autoProfile['aws_role_arn'], RoleSessionName=autoProfile['awsume_session_name'])
        session = response['Credentials']
        session['Expiration'] = session['Expiration'].astimezone(dateutil.tz.tzlocal())
        session['Expiration'] = session['Expiration'].strftime('%Y-%m-%d %H:%M:%S')
        session['region'] = sourceCredentials['region']

        autoProfile['aws_access_key_id'] = session['AccessKeyId']
        autoProfile['aws_secret_access_key'] = session['SecretAccessKey']
        autoProfile['aws_session_token'] = session['SessionToken']
        autoProfile['awsume_role_expiration'] = session['Expiration']
        awsumepy.write_auto_awsume_session(autoProfile['__name__'].replace('auto-refresh-', ''), autoProfile, AWS_CREDENTIALS_FILE)
    except botocore.exceptions.ClientError:
        pass

def extract_auto_refresh_profiles(profiles):
    """Pull out any profiles with the prefix 'auto-refresh-' in the name.

    Parameters
    ----------
    - profiles - the profiles read from the aws credentials file

    Returns
    -------
    A dict of profiles that are prefixed by 'auto-refresh-' in the name.
    """
    autoRefreshProfiles = {}
    for profile in profiles:
        if 'auto-refresh-' in profile:
            autoRefreshProfiles[profile] = profiles[profile]
    return autoRefreshProfiles

def get_earliest_expiration(autoProfiles):
    """Get the earliest expiration from the autoProfiles

    Parameters
    ----------
    - autoProfiles - the autoawsume profiles from the credentials profile

    Returns
    -------
    A datetime object containing the earliest expiration.
    """
    expirations = []
    for profile in autoProfiles:
        expirations.append(
            datetime.datetime.strptime(
                autoProfiles[profile]['awsume_user_expiration'], '%Y-%m-%d %H:%M:%S'))
        expirations.append(
            datetime.datetime.strptime(
                autoProfiles[profile]['awsume_role_expiration'], '%Y-%m-%d %H:%M:%S'))
    if expirations:
        return min(expirations)
    else:
        return get_now()

def refresh_expired_profiles(autoProfiles):
    """Refresh any expired autoProfiles.

    Parameters
    ----------
    - autoProfiles - the autoawsume profiles from the credentials profile
    """
    for profile in autoProfiles:
        userExpiration = datetime.datetime.strptime(autoProfiles[profile]['awsume_user_expiration'], '%Y-%m-%d %H:%M:%S')
        roleExpiration = datetime.datetime.strptime(autoProfiles[profile]['awsume_role_expiration'], '%Y-%m-%d %H:%M:%S')
        if roleExpiration < get_now():
            refresh_session(autoProfiles[profile])
        if userExpiration < get_now():
            awsumepy.remove_auto_profile(autoProfiles[profile]['__name__'].replace('auto-refresh-', ''))

def main():
    while True:
        credentialsProfiles = awsumepy.read_ini_file(AWS_CREDENTIALS_FILE)
        autoRefreshProfiles = extract_auto_refresh_profiles(credentialsProfiles)
        refresh_expired_profiles(autoRefreshProfiles)
        earliestExpiration = get_earliest_expiration(autoRefreshProfiles)
        timeUntilEarliestExpiration = (earliestExpiration - get_now().replace(tzinfo=earliestExpiration.tzinfo)).total_seconds()
        if timeUntilEarliestExpiration <= 0:
            break
        # awsumepy.safe_print("autoawsume: Sleeping for " + str(timeUntilEarliestExpiration) + " seconds", file=sys.stderr)
        time.sleep(timeUntilEarliestExpiration)
    # awsumepy.safe_print("autoawsume: No more credentials left to refresh, shutting down", file=sys.stderr)

if __name__ == '__main__': # pragma: no cover
    main()
