from __future__ import print_function
import sys
import datetime
import time
from awsume import awsumepy
from awsume.awsumepy import AWS_CACHE_DIRECTORY, AWS_CREDENTIALS_FILE

def refresh_session(oldSession, roleArn, sessionName):
    """
    oldSession - the session to refresh;
    roleArn - the role_arn used to make the assume_role call;
    sessionName - what to name the assumed role session;
    refresh the `oldSession` role credentials and return them
    """
    #create the client to make aws calls
    refreshClient = awsumepy.create_boto_sts_client(None,
                                                    oldSession['SecretAccessKey'],
                                                    oldSession['AccessKeyId'],
                                                    oldSession['SessionToken'])
    #call assume_role
    roleCredentials = awsumepy.get_assume_role_credentials(refreshClient,
                                                           roleArn,
                                                           sessionName)
    #format the credentials for awsume
    newRoleSession = awsumepy.create_awsume_session(roleCredentials, oldSession)
    #localize the expiration
    newRoleSession['Expiration'] = newRoleSession['Expiration'].replace(tzinfo=None)
    return newRoleSession

def scan_through_auto_refresh_profiles(credentialsProfiles):
    """
    credentialsProfiles - the dict of profiles to scan through;
    loop through the `credentialsProfiles`, find any that are 'auto-refresh-' profiles,
    refresh/remove any expired ones, and return when the earliest session-expiration will happen
    """
    for profile in credentialsProfiles:
        expirationList = []
        #if we're looking at an auto-refreshed profile
        if 'auto-refresh-' in profile:
            #get the cache filename (the file that contains source_profile credentials)
            cacheFileName = credentialsProfiles[profile]['awsume_cache_file']
            #get the source profile's credentials
            sourceProfileCredentials = awsumepy.read_awsume_session_from_file(AWS_CACHE_DIRECTORY, cacheFileName)

            #if credentials are not expired
            if sourceProfileCredentials['Expiration'] > datetime.datetime.now():
                try:
                    #refresh the session
                    refreshedCredentials = refresh_session(sourceProfileCredentials, credentialsProfiles[profile]['aws_role_arn'], profile.replace('auto-awsume-', '') + '-auto-awsume-session')
                except Exception as e:
                    #if refreshing the session failed, remove that profile
                    print("autoAwsume: Refreshing profile [" + profile.replace('auto-refresh-', '') + "] failed. That profile will no longer be auto-refreshed.")
                    print(str(e))
                    awsumepy.remove_auto_awsume_profile_by_name(profile.replace('auto-refresh-',''), AWS_CREDENTIALS_FILE)
                else:
                    #write the session
                    awsumepy.write_auto_awsume_session(profile, refreshedCredentials, cacheFileName, credentialsProfiles[profile]['aws_role_arn'], AWS_CREDENTIALS_FILE)
                    expirationList.append(min(sourceProfileCredentials['Expiration'], refreshedCredentials['Expiration']))
            #if credentials are expired
            else:
                awsumepy.remove_auto_awsume_profile_by_name(profile.replace('auto-refresh-',''), AWS_CREDENTIALS_FILE)
    if expirationList:
        return min(expirationList)
    else:
        return datetime.datetime.now()

def main():
    while True:
        #get the list of profiles
        autoAwsumeProfiles = awsumepy.get_profiles_from_ini_file(AWS_CREDENTIALS_FILE)
        #look for the earliest expiration and if possible, refresh any expired sessions
        earliestExpiration = scan_through_auto_refresh_profiles(autoAwsumeProfiles)
        #calculate the time until the earliest expiration
        timeUntilEarliestExpiration = (earliestExpiration - datetime.datetime.now().replace(tzinfo=earliestExpiration.tzinfo)).total_seconds()
        #if that time has already expired
        if timeUntilEarliestExpiration <= 0:
            break
        #wait until the next session expires to run again
        time.sleep(timeUntilEarliestExpiration)

    print("#autoAwsume: No more credentials left to refresh, shutting down", file=sys.stderr)

if __name__ == '__main__':
    main()
