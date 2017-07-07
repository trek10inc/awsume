
__version__ = '1.1.2'

import sys, os, ConfigParser, re, argparse, collections, datetime, dateutil, boto3, psutil

#get cross-platform home directory
HOME_PATH = os.path.expanduser('~')
AWS_CONFIG_FILE = HOME_PATH + '/.aws/config'
AWS_CREDENTIALS_FILE = HOME_PATH + '/.aws/credentials'
AWS_CACHE_DIRECTORY = HOME_PATH + '/.aws/cli/cache/'

def parse_arguments(commandLineArguments):
    """
    commandLineArguments - a list of arguments;
    parse through the arguments
    """
    commandLineArgParser = argparse.ArgumentParser(description='AWSume')
    #profile name argument
    commandLineArgParser.add_argument(action='store', dest='profile_name',
                                      nargs='?', metavar='profile name',
                                      help='The profile name')
    #default flag
    commandLineArgParser.add_argument('-d', action='store_true', default='False',
                                      dest='default',
                                      help='Use the default profile')
    #show flag (only used for the shell wrapper)
    commandLineArgParser.add_argument('-s', action='store_true', default=False,
                                      dest='show',
                                      help='Show the commands to assume the role')
    #refresh flag
    commandLineArgParser.add_argument('-r', action='store_true', default=False,
                                      dest='refresh',
                                      help='Force refresh the session')
    #auto-refresh flag
    commandLineArgParser.add_argument('-a', action='store_true', default=False,
                                      dest='auto_refresh',
                                      help='Enable auto-refreshing role credentials')
    #kill auto-refresher flag
    commandLineArgParser.add_argument('-k', action='store_true', default=False,
                                      dest='kill',
                                      help='Kill the auto-refreshing process')
    #display version flag
    commandLineArgParser.add_argument('-v', action='store_true', default=False,
                                      dest='version',
                                      help='Display the current version of AWSume')
    #list profiles flag
    commandLineArgParser.add_argument('-l', action='store_true', default=False,
                                      dest='list_profiles',
                                      help='List useful information about available profiles')
    return commandLineArgParser.parse_args(commandLineArguments)

def handle_command_line_arguments(arguments):
    """
    arguments - the arguments to handle;
    scan the arguments for anything special that only requires one function call and then exit
    """
    #check for version flag
    if arguments.version:
        print 'Version' + ' ' + __version__
        exit(0)

    #check for list profiles flag
    if arguments.list_profiles:
        list_profile_data()
        exit(0)

    #check for the kill auto-refresher flag
    if arguments.kill:
        stop_auto_refresh(arguments.profile_name)
        exit(0)

    if arguments.default is True or arguments.profile_name is None or arguments.profile_name == 'default':
        #make sure we always look at the default profile
        arguments.profile_name = 'default'
        arguments.default = True

def get_profiles_from_ini_file(iniFilePath):
    """
    iniFilePath - the file to create a parser out of;
    return a dict of sections from the file
    """
    if os.path.exists(iniFilePath):
        iniFileParser = ConfigParser.ConfigParser()
        iniFileParser.read(iniFilePath)
        return iniFileParser._sections
    print >> sys.stderr, '#AWSume Error: Trying to access non-existant file path: ' + iniFilePath
    exit(1)

def get_ini_profile_by_name(iniProfileName, iniProfiles):
    """
    iniProfileName - the name of the profile to return;
    iniProfiles - the dict of ini profiles to search through;
    return the profile under the name given by `iniProfileName`
    """
    #check if profile exists
    if iniProfileName in iniProfiles:
        return iniProfiles[iniProfileName]
    #if profile doesn't exist, return an empty OrderedDict
    return collections.OrderedDict()

def get_config_profile(arguments):
    """
    arguments - the command-line arguments;
    return the config profile from the given command-line arguments
    """
    if arguments.default is True:
        return get_ini_profile_by_name('default', get_profiles_from_ini_file(AWS_CONFIG_FILE))
    else:
        return get_ini_profile_by_name('profile ' + arguments.profile_name, get_profiles_from_ini_file(AWS_CONFIG_FILE))

def get_credentials_profile(configSection, arguments):
    """
    configSection - the config profile that tells which credentials profile to get;
    arguments - the command-line arguments;
    return the appropriate credentials file, whether `configSection` is a role or user profile
    """
    #get the credentials file, whether that be a source_profile or the other half of a user profile
    if is_role_profile(configSection):
        #grab the source profile
        return get_source_profile_from_role(configSection, AWS_CREDENTIALS_FILE)
    else:
        #the rest of the user, from the credentials file
        returnProfile = get_ini_profile_by_name(arguments.profile_name, get_profiles_from_ini_file(AWS_CREDENTIALS_FILE))
        if returnProfile == collections.OrderedDict():
            print >> sys.stderr, '#AWSume Error: Profile not found in credentials file'
            exit(1)
        return returnProfile

def validate_profiles(configSection, credentialsSection):
    """
    configSection - the config profile from the config file;
    credentialsSection - the credentials profile from the credentials file;
    check that `configSection` and `credentialsSection` is valid, if not exit
    """
    #if the profile doesn't exist, leave
    if not configSection and not credentialsSection:
        print >> sys.stderr, '#AWSume Error: Profile not found'
        exit(1)
    #make sure credentials profile has its credentials
    validate_credentials_profile(credentialsSection)

def handle_profiles(configSection, credentialsSection):
    """
    configSection - the config profile from the config file;
    credentialsSection - the credentials profile from the credentials file;
    validate profiles and check for any special cases
    """
    #validate the profiles
    validate_profiles(configSection, credentialsSection)

    #if the user is AWSuming a user profile, and no mfa is required
    #no more work is required
    if not is_role_profile(configSection) and 'mfa_serial' not in configSection:
        print 'Awsume' +  ' ' + \
                credentialsSection.get('aws_secret_access_key') + ' ' + \
                'None' + ' ' + \
                credentialsSection.get('aws_access_key_id') + ' ' + \
                str(configSection.get('region')) #region may or may not be 'NoneType'
        exit(0)

def get_awsume_user_credentials(configSection, credentialsSection, arguments):
    """
    configSection - the profile from the config file;
    credentialsSection - the profile from the credentials file;
    arguments - the command-line arguments passed into AWSume
    """
    cacheFileName = 'awsume-temp-' + credentialsSection['__name__']
    cacheSession = read_awsume_session_from_file(AWS_CACHE_DIRECTORY, cacheFileName)
    #verify the expiration, or if the user wants to force-refresh
    if arguments.refresh or not is_valid_awsume_session(cacheSession):
        #the boto3 client used to make aws calls
        userClient = create_boto_sts_client(credentialsSection['__name__'])
        #set the session
        awsUserSession = get_session_token_credentials(userClient, configSection)
        userSession = create_awsume_session(awsUserSession, configSection)
        write_awsume_session_to_file(AWS_CACHE_DIRECTORY, cacheFileName, userSession)
        print >> sys.stderr, '#User profile credentials will expire: ' + str(userSession['Expiration'])
        return userSession
    else:
        print >> sys.stderr, '#User profile credentials will expire: ' + str(cacheSession['Expiration'])
        return cacheSession

def get_awsume_role_credentials(configSection, userSession):
    """
    configSection - the profile from the config file;
    userSession - the session credentials for the user calling assume_role;
    get awsume-formatted role credentials from calling assume_role with `userSession` credentials
    """
    #create new client based on the new session credentials
    roleClient = create_boto_sts_client(None,
                                        userSession['SecretAccessKey'],
                                        userSession['AccessKeyId'],
                                        userSession['SessionToken'])
    #assume the role
    awsRoleSession = get_assume_role_credentials(roleClient,
                                                 configSection['role_arn'],
                                                 configSection['__name__'].replace('profile ', '') + '-awsume-session')

    roleSession = create_awsume_session(awsRoleSession, configSection)
    return roleSession

def start_auto_refresher(arguments, userSession, configSection, credentialsSection):
    """
    arguments - the command-line arguments passed into AWSume;
    userSession - the session credentials for the user to call assume_role with;
    configSection - the profile from the config file;
    credentialsSection - the profile from the credentials file
    """
    cacheFileName = 'awsume-temp-' + credentialsSection['__name__']

    #create a profile in credentials file to store session credentials
    autoAwsumeProfileName = 'auto-refresh-' + arguments.profile_name
    write_auto_awsume_session(autoAwsumeProfileName, userSession, cacheFileName, configSection['role_arn'])

    #kill all autoAwsume processes before starting a new one
    kill_all_auto_processes()
    print 'Auto' + ' ' + autoAwsumeProfileName + ' ' + cacheFileName
    exit(0)

def handle_getting_role_credentials(configSection, credentialsSection, userSession, arguments):
    """
    configSection - the profile from the config file;
    credentialsSection - the profile from the credentials file;
    userSession - the session credentials for the user to call assume_role with;
    arguments - the command-line arguments passed into AWSume
    """
    if is_role_profile(configSection):
        #if the user wants to auto-refresh the role credentials
        if arguments.auto_refresh is True:
            start_auto_refresher(arguments, userSession, configSection, credentialsSection)
        #if the user is assuming a role normally
        else:
            roleSession = get_awsume_role_credentials(configSection, userSession)
            print >> sys.stderr, '#Role profile credentials will expire: ' + str(roleSession['Expiration'])
            return roleSession
    else:
        if arguments.auto_refresh is True:
            print >> sys.stderr, '#Using user credentials, autoAwsume will not run.'
        return None

def validate_credentials_profile(awsumeCredentialsProfile):
    """
    awsumeCredentialsProfile - the profile to validate;
    validate that `awsumeConfigProfile` has proper aws credentials;
    if not, print an error and exit
    """
    if 'aws_access_key_id' not in awsumeCredentialsProfile:
        print >> sys.stderr, '#AWSume Error: Your profile does not contain an access key id'
        exit(1)
    if 'aws_secret_access_key' not in awsumeCredentialsProfile:
        print >> sys.stderr, '#AWSume Error: Your profile does not contain a secret access key'
        exit(1)

def get_source_profile_from_role(givenProfile, sourceProfileFilePath):
    """
    givenProfile - the profile that should contains the source profile name;
    sourceProfileFilePath - the file that contains the source profile of `givenProfile`;
    return the source profile of `givenProfile`, if there is no source_profile, return empty OrderedDict
    """
    if os.path.exists(sourceProfileFilePath):
        if is_role_profile(givenProfile):
            sourceProfile = get_ini_profile_by_name(givenProfile['source_profile'], get_profiles_from_ini_file(sourceProfileFilePath))
            if sourceProfile != collections.OrderedDict():
                return sourceProfile
            print >> sys.stderr, '#AWSume Error: Profile does not contain a valid source profile'
            exit(1)
        return collections.OrderedDict()
    print >> sys.stderr, '#AWSume Error: Trying to access non-existant file path: ' + sourceProfileFilePath
    exit(1)

def is_role_profile(profileToCheck):
    """
    profileToCheck - the profile to check;
    return if `profileToCheck` is a role or user
    """
    #if both 'source_profile' and 'role_arn' are in the profile, then it is a role profile
    if 'source_profile' in profileToCheck and 'role_arn' in profileToCheck:
        return True
    #if the profile has one of them, but not the other
    if 'source_profile' in profileToCheck:
        print >> sys.stderr, '#AWSume Error: Profile contains a source_profile, but no role_arn'
        exit(1)
    if 'role_arn' in profileToCheck:
        print >> sys.stderr, '#AWSume Error: Profile contains a role_arn, but no source_profile'
        exit(1)
    #if 'source_profile' and 'role_arn' are not in the profile, it is a user profile
    return False

def read_mfa():
    """
    prompt the user to enter an MFA code;
    return the string entered by the user
    """
    print >> sys.stderr, '#Enter MFA Code:'
    return raw_input()

def is_valid_mfa_token(mfaToken):
    """
    mfaToken - the token to validate;
    return if `mfaToken` is a valid MFA code
    """
    #compare the given token with the regex
    mfaTokenPattern = re.compile('^[0-9]{6}$')
    if not mfaTokenPattern.match(mfaToken):
        return False
    return True

def create_boto_sts_client(profileName=None, secretAccessKey=None, accessKeyId=None, sessionToken=None):
    """
    profileName - the name of the profile to create the client with;
    secretAccessKey - secret access key that can be passed into the session;
    accessKeyId - access key id that can be passed into the session;
    sessionToken - session token that can be passed into the session;
    return a boto3 session client
    """
    #establish the boto session with given credentials
    botoSession = boto3.Session(profile_name=profileName,
                                aws_access_key_id=accessKeyId,
                                aws_secret_access_key=secretAccessKey,
                                aws_session_token=sessionToken)
    #create an sts client, always defaulted to us-east-1
    return botoSession.client('sts', region_name='us-east-1')

def get_session_token_credentials(getSessionTokenClient, awsumeProfile):
    """
    getSessionTokenClient - the client to make the call on;
    awsumeProfile - an awsume-formatted profile;
    return the session token credentials
    """
    #if the profile doesn't have an mfa_serial entry,
    #mfa isn't required, so just call get_session_token
    if 'mfa_serial' not in awsumeProfile:
        return getSessionTokenClient.get_session_token()
    else:
        #get the mfa arn
        mfaSerial = awsumeProfile['mfa_serial']
        #get mfa token
        mfaToken = read_mfa()
        if not is_valid_mfa_token(mfaToken):
            print >> sys.stderr, '#Invalid MFA Code'
            exit(1)
        #make the boto sts get_session_token call
        try:
            return getSessionTokenClient.get_session_token(
                SerialNumber=mfaSerial,
                TokenCode=mfaToken)

        except boto3.exceptions.botocore.exceptions.ClientError as e:
            print >> sys.stderr, '#AWSume Error: ' + str(e)
            exit(1)

def get_assume_role_credentials(assumeRoleClient, roleArn, roleSessionName):
    """
    assumeRoleClient - the client to make the sts call on;
    roleArn - the role arn to use when assuming the role;
    roleSessionName - the name to assign to the role-assumed session;
    assume role and return the session credentials
    """
    try:
        return assumeRoleClient.assume_role(
            RoleArn=roleArn,
            RoleSessionName=roleSessionName)

    except boto3.exceptions.botocore.exceptions.ClientError as e:
        print >> sys.stderr, '#AWSume Error: ' + str(e)
        exit(1)

def create_awsume_session(awsCredentialsProfile, awsIniProfile):
    """
    awsCredentialsProfile - contains the credentials required for setting the session;
    awsIniProfile - contains the region required for setting the session;
    returns an awsume-formatted session as a dict
    """
    #if the role is invalid
    if awsCredentialsProfile.get('Credentials'):
        #create the awsume session
        awsumeSession = collections.OrderedDict()
        awsumeSession['SecretAccessKey'] = awsCredentialsProfile.get('Credentials').get('SecretAccessKey')
        awsumeSession['SessionToken'] = awsCredentialsProfile.get('Credentials').get('SessionToken')
        awsumeSession['AccessKeyId'] = awsCredentialsProfile.get('Credentials').get('AccessKeyId')
        awsumeSession['region'] = awsIniProfile.get('region')
        awsumeSession['Expiration'] = awsCredentialsProfile.get('Credentials').get('Expiration')
        #convert the time to local time
        if awsumeSession.get('Expiration'):
            if awsumeSession['Expiration'].tzinfo != None:
                awsumeSession['Expiration'] = awsumeSession['Expiration'].astimezone(dateutil.tz.tzlocal())
        return awsumeSession
    print >> sys.stderr, '#AWSume Error: Invalid Credentials'
    exit(1)

def session_string(awsumeSession):
    """
    awsumeSession - the session to create a string out of;
    create a formatted and space-delimited string containing useful credential information;
    if an empty session is given, an empty string is returned
    """
    if all(cred in awsumeSession for cred in ('SecretAccessKey', 'SessionToken', 'AccessKeyId', 'region')):
        return str(awsumeSession['SecretAccessKey']) + ' ' + \
            str(awsumeSession['SessionToken']) + ' ' + \
            str(awsumeSession['AccessKeyId']) + ' ' + \
            str(awsumeSession['region'])
    return ''

def parse_session_string(sessionString):
    """
    sessionString - the formatted string that contains session credentials;
    return a session dict containing the session credentials contained in `sessionString`;
    if `sessionString` is invalid, an empty dict will be returned
    """
    sessionArray = sessionString.split(' ')
    awsumeSession = collections.OrderedDict()
    if len(sessionArray) == 5:
        awsumeSession['SecretAccessKey'] = sessionArray[0]
        awsumeSession['SessionToken'] = sessionArray[1]
        awsumeSession['AccessKeyId'] = sessionArray[2]
        awsumeSession['region'] = sessionArray[3]
        if sessionArray[4] != 'None':
            awsumeSession['Expiration'] = datetime.datetime.strptime(sessionArray[4], '%Y-%m-%d_%H-%M-%S')
    return awsumeSession

def write_awsume_session_to_file(cacheFilePath, cacheFileName, awsumeSession):
    """
    cacheFilePath - the path to write the cache file to;
    cacheFileName - the name of the file to write;
    awsumeSession - the session to write;
    write the session to the file path
    """
    if not os.path.exists(cacheFilePath):
        os.makedirs(cacheFilePath)
    out_file = open(cacheFilePath + cacheFileName, 'w+')
    if awsumeSession.get('Expiration'):
        out_file.write(session_string(awsumeSession) + ' ' + awsumeSession['Expiration'].strftime('%Y-%m-%d_%H-%M-%S'))
    else:
        out_file.write(session_string(awsumeSession) + ' ' + str(None))
    out_file.close()

def read_awsume_session_from_file(cacheFilePath, cacheFileName):
    """
    cacheFilePath - the path to read from;
    cacheFilename - the name of the cache file;
    return a session if the path to the file exists
    """
    if os.path.isfile(cacheFilePath + cacheFileName):
        in_file = open(cacheFilePath + cacheFileName, 'r')
        awsumeSession = parse_session_string(in_file.read())
    else:
        awsumeSession = collections.OrderedDict()
    return awsumeSession

def is_valid_awsume_session(awsumeSession):
    """
    awsumeSession - the session to validate;
    return whether or not the session is valid;
    if credentials are expired, or don't exist, they're invalid;
    else they are valid
    """
    #check if the session has an expiration
    if awsumeSession.get('Expiration'):
        #check if the session is expired
        if awsumeSession.get('Expiration') > datetime.datetime.now().replace():
            return True
        return False
    return False

def write_auto_awsume_session(autoAwsumeName, awsumeSession, awsumeCacheFile, roleArn):
    """
    autoAwsumeName - the name of the section we are going to write;
    awsumeSession - the session we are going to write under the section;
    awsumeCacheFile - the name of the cache file for the auto-refresh to reference;
    roleArn - the auto-refresher needs this to be able to assume the role;
    add `awsumeSession` under the name `autoAwsumeName` to the credentials file;
    if the section already exists, remove and replace with the new one
    """
    #check to see if profile exists
    autoAwsumeParser = ConfigParser.ConfigParser()
    autoAwsumeParser.read(AWS_CREDENTIALS_FILE)
    #if the section already exists, remove it to overwrite
    if autoAwsumeParser.has_section(autoAwsumeName):
        autoAwsumeParser.remove_section(autoAwsumeName)
    #place the new session credentials in the file
    autoAwsumeParser.add_section(autoAwsumeName)
    autoAwsumeParser.set(autoAwsumeName, 'aws_session_token', awsumeSession['SessionToken'])
    autoAwsumeParser.set(autoAwsumeName, 'aws_security_token', awsumeSession['SessionToken'])
    autoAwsumeParser.set(autoAwsumeName, 'aws_access_key_id', awsumeSession['AccessKeyId'])
    autoAwsumeParser.set(autoAwsumeName, 'aws_secret_access_key', awsumeSession['SecretAccessKey'])
    autoAwsumeParser.set(autoAwsumeName, 'awsume_cache_file', awsumeCacheFile)
    autoAwsumeParser.set(autoAwsumeName, 'aws_role_arn', roleArn)

    if awsumeSession['region'] != 'None':
        autoAwsumeParser.set(autoAwsumeName, 'region', awsumeSession['region'])
        autoAwsumeParser.set(autoAwsumeName, 'default_region', awsumeSession['region'])
    #write our changes to the file
    autoAwsumeParser.write(open(AWS_CREDENTIALS_FILE, 'w'))

def kill_all_auto_processes():
    """
    kill all running autoAwsume processes
    """
    for proc in psutil.process_iter():
        try:
            #kill the autoAwsume process if no more auto-refresh profiles remain
            process_command = proc.cmdline()
            for command_string in process_command:
                if 'autoAwsume' in command_string:
                    #the profile and default_profile environment variables
                    proc.kill()
        except Exception:
            pass

def remove_all_auto_profiles():
    """
    remove all profiles from the credentials file that contain 'auto-refresh-'
    """
    #remove the auto-awsume profiles from the credentials file
    autoAwsumeProfileParser = ConfigParser.ConfigParser()
    autoAwsumeProfileParser.read(AWS_CREDENTIALS_FILE)
    #scan all profiles to find auto-refresh profiles
    for profile in autoAwsumeProfileParser._sections:
        if 'auto-refresh-' in profile:
            autoAwsumeProfileParser.remove_section(profile)
    #save changes
    autoAwsumeProfileParser.write(open(AWS_CREDENTIALS_FILE, 'w'))

def remove_auto_awsume_profile_by_name(profileName):
    """
    remove only the given auto-awsume profile from the credentials file
    """
    autoAwsumeProfileParser = ConfigParser.ConfigParser()
    autoAwsumeProfileParser.read(AWS_CREDENTIALS_FILE)
    #scan all profiles to find auto-refresh profiles
    for profile in autoAwsumeProfileParser._sections:
        if profile == 'auto-refresh-' + profileName:
            autoAwsumeProfileParser.remove_section(profile)
    #save changes
    autoAwsumeProfileParser.write(open(AWS_CREDENTIALS_FILE, 'w'))

def is_auto_refresh_profiles():
    """
    return whether or not there is any auto-refresh profiles
    """
    autoAwsumeProfileParser = ConfigParser.ConfigParser()
    autoAwsumeProfileParser.read(AWS_CREDENTIALS_FILE)

    #scan all profiles to find auto-refresh profiles
    for profile in autoAwsumeProfileParser._sections:
        if 'auto-refresh-' in profile:
            return True
    return False

def stop_auto_refresh(profileName=None):
    """
    profileName - the profile to stop auto-refreshing for;
    clean up autoAwsume's mess, kill autoAwsume, and exit
    """
    if profileName is None:
        remove_all_auto_profiles()
    else:
        remove_auto_awsume_profile_by_name(profileName)
    #if no more auto-refresh profiles remain, kill the process
    if not is_auto_refresh_profiles():
        kill_all_auto_processes()
        print 'Kill'
    exit(0)

def generate_formatted_data(configSections):
    """
    configSections - the profile from the config file;
    format the config profiles for easy printing
    """
    #list headers
    profileList = []
    profileList.append([])
    profileList[0].append('PROFILE')
    profileList[0].append('TYPE')
    profileList[0].append('SOURCE')
    profileList[0].append('MFA?')
    profileList[0].append('REGION')
    #now fill the tables with the appropriate data
    index = 1
    for section in configSections:
        if is_role_profile(configSections[section]):
            profileList.append([])
            profileList[index].append(section.replace('profile ', ''))
            profileList[index].append('Role')
            profileList[index].append(configSections[section]['source_profile'])
            profileList[index].append('Yes' if 'mfa_serial' in configSections[section] else 'No')
            profileList[index].append(str(configSections[section].get('region')))
        else:
            profileList.append([])
            profileList[index].append(section.replace('profile ', ''))
            profileList[index].append('User')
            profileList[index].append('None')
            profileList[index].append('Yes' if 'mfa_serial' in configSections[section] else 'No')
            profileList[index].append(str(configSections[section].get('region')))
        index += 1
    return profileList

def print_formatted_data(formattedProfileData):
    """
    formattedProfileData - the data to display, formatted;
    display `formattedProfileData` in a nice, proper way
    """
    widths = [max(map(len, col)) for col in zip(*formattedProfileData)]
    print >> sys.stderr, ""
    print >> sys.stderr, 'AWS Profiles'.center(sum(widths) + 8, '=')
    for row in formattedProfileData:
        print >> sys.stderr, "  ".join((val.ljust(width) for val, width in zip(row, widths)))

def list_profile_data():
    """
    List useful information about awsume-able profiles
    """
    configSections = get_profiles_from_ini_file(AWS_CONFIG_FILE)
    print_formatted_data(generate_formatted_data(configSections))

def main():
    #get command-line arguments and handle them
    commandLineArguments = parse_arguments(sys.argv[1:])
    #handle command-line arguments
    handle_command_line_arguments(commandLineArguments)

    #get the two profiles
    configProfile = get_config_profile(commandLineArguments)
    credentialsProfile = get_credentials_profile(configProfile, commandLineArguments)

    #handle those profiles
    handle_profiles(configProfile, credentialsProfile)

    #now we have to get the session token
    awsumeUserSession = get_awsume_user_credentials(configProfile, credentialsProfile, commandLineArguments)
    sessionToUse = awsumeUserSession

    awsumeRoleSession = handle_getting_role_credentials(configProfile, credentialsProfile, awsumeUserSession, commandLineArguments)
    #if the role session is valid
    if awsumeRoleSession:
        sessionToUse = awsumeRoleSession

    #send shell script wrapper the session environment variables
    print 'Awsume' + ' ' + session_string(sessionToUse)

if __name__ == '__main__':
    main()
