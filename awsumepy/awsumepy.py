import sys, os, ConfigParser, re, argparse, collections, datetime, dateutil, boto3

#get cross-platform home directory
HOME_PATH = os.path.expanduser('~')

def handle_parameters(arguments):
    """
    arguments - a list of arguments
    parse through the arguments
    return a namespace
    """
    parser = argparse.ArgumentParser(description='Awsume')
    #profile name argument
    parser.add_argument(action='store', dest='profile_name',
                        nargs='?', default='default',
                        metavar='profile name',
                        help='The profile name')
    #default flag
    parser.add_argument('-d', action='store_true', default='False',
                        dest='default',
                        help='Use the default profile')
    #show flag (only used for the shell wrapper)
    parser.add_argument('-s', action='store_true', default=False,
                        dest='show',
                        help='Show the commands to assume the role')
    #refresh flag
    parser.add_argument('-r', action='store_true', default=False,
                        dest='refresh',
                        help='Force refresh the session')
    return parser.parse_args(arguments)

def get_sections(iniFile):
    """
    iniFile - the file to create a parser out of
    return a dict of sections from the file
    """
    if os.path.exists(iniFile):
        PARSER = ConfigParser.ConfigParser()
        PARSER.read(iniFile)
        return PARSER._sections
    print >> sys.stderr, '#Error::invalid file path'
    exit(1)

def get_section(sectionName, sections):
    """
    sectionName - the name of a section to get
    sections - the sections to search in
    return the section under the name `sectionName`
    """
    #check if profile exists
    if sectionName in sections:
        return sections[sectionName]
    return collections.OrderedDict()

def validate_credentials_profile(awsumeCredentialsProfile):
    """
    awsumeConfigProfile - the profile to validate
    validate that `awsumeConfigProfile` has proper aws credentials
    """
    if 'aws_access_key_id' not in awsumeCredentialsProfile:
        print >> sys.stderr, '#Error: Your profile does not contain an access key id'
        exit(1)
    if 'aws_secret_access_key' not in awsumeCredentialsProfile:
        print >> sys.stderr, '#Error: Your profile does not contain a secret access key'
        exit(1)

def get_source_profile(userProfile, sourceFilePath):
    """
    userProfile - the profile that contains the source profile name
    sourceFilePath - the file that contains the source profile of `userProfile`
    return the source profile of `userProfile`, if there is no source_profile, return empty OrderedDict
    """
    if os.path.exists(sourceFilePath):
        if is_role(userProfile):
            returnProfile = get_section(userProfile['source_profile'], get_sections(sourceFilePath))
            if returnProfile != collections.OrderedDict():
                return returnProfile
            print >> sys.stderr, '#Error: Profile does not contain a valid source profile'
            exit(1)
        return collections.OrderedDict()
    print >> sys.stderr, '#Error: Trying to access non-existant file path: ' + sourceFilePath
    exit(1)

def is_role(profileToCheck):
    """
    profileToCheck - the profile to check
    return if `profileToCheck` is a role or user
    """
    if 'source_profile' in profileToCheck and 'role_arn' in profileToCheck:
        return True
    if 'source_profile' in profileToCheck:
        print >> sys.stderr, '#Error: Profile contains a source_profile, but no role_arn'
        exit(1)
    if 'role_arn' in profileToCheck:
        print >> sys.stderr, '#Error: Profile contains a role_arn, but no source_profile'
        exit(1)
    return False

def read_mfa():
    """
    prompt the user to enter an MFA code
    return the string entered by the user
    """
    print >> sys.stderr, '#Enter MFA Code:'
    return raw_input()

def valid_mfa_token(mfaToken):
    """
    mfaToken - the token to validate
    return if `mfaToken` is a valid MFA code
    """
    mfaTokenPattern = re.compile('^[0-9]{6}$')
    if not mfaTokenPattern.match(mfaToken):
        return False
    return True

def create_client(profileName=None, secretAccessKey=None, accessKeyId=None, sessionToken=None):
    """
    profileName - the name of the profile to create the client with
    secretAccessKey - secret access key that can be passed into the session
    accessKeyId - access key id that can be passed into the session
    sessionToken - session token that can be passed into the session
    return a boto3 session client
    """
    botoSession = boto3.Session(profile_name=profileName,
                                aws_access_key_id=accessKeyId,
                                aws_secret_access_key=secretAccessKey,
                                aws_session_token=sessionToken)

    return botoSession.client('sts', region_name='us-east-1')

def get_session(getSessionTokenClient, awsumeProfile):
    """
    getSessionTokenClient - the client to make the call on
    awsumeProfile - the profile to 'awsume'
    return the session token credentials
    """
    #if the profile doesn't have an mfa_serial entry
    if 'mfa_serial' not in awsumeProfile:
        return getSessionTokenClient.get_session_token()
    else:
        mfaSerial = awsumeProfile['mfa_serial']
        #get mfa token
        mfaToken = read_mfa()
        if not valid_mfa_token(mfaToken):
            print >> sys.stderr, '#Invalid MFA Code'
            exit(1)
        #make call
        try:
            return getSessionTokenClient.get_session_token(
                SerialNumber=mfaSerial,
                TokenCode=mfaToken
            )
        except boto3.exceptions.botocore.exceptions.ClientError as e:
            print >> sys.stderr, "#Error: " + str(e)
            exit(1)

def assume_role(assumeRoleClient, roleArn, roleSessionName):
    """
    assumeRoleClient - the client to make the sts call on
    roleArn - the role arn to use when assuming the role
    roleSessionName - the name to assign to the role-assumed session
    assume role and return the session credentials
    """
    try:
        return assumeRoleClient.assume_role(
            RoleArn=roleArn,
            RoleSessionName=roleSessionName
       )
    except boto3.exceptions.botocore.exceptions.ClientError as e:
        print >> sys.stderr, "#Error: " + str(e)
        print >> sys.stderr, "#This is likely because your config role profile does not have an `mfa_serial` listed when it needs one to assume the role."
        print >> sys.stderr, "#Please verify that all information in your config and credentials file is correct. Consult the AWS documentation to verify."
        print >> sys.stderr, "#You may also have to clear the cache for this profile, as it may contain non-MFA authenticated credentials"
        exit(1)

def create_awsume_session(awsRole, awsProfile):
    """
    awsRole - contains the credentials required for setting the session
    awsProfile - contains the region required for setting the session
    returns a dict of the session to set
    """
    awsumeSession = collections.OrderedDict()
    if awsRole.get('Credentials'):
        awsumeSession['SecretAccessKey'] = awsRole.get('Credentials').get('SecretAccessKey')
        awsumeSession['SessionToken'] = awsRole.get('Credentials').get('SessionToken')
        awsumeSession['AccessKeyId'] = awsRole.get('Credentials').get('AccessKeyId')
        awsumeSession['region'] = awsProfile.get('region')
        awsumeSession['Expiration'] = awsRole.get('Credentials').get('Expiration')
        #convert the time to local time
        if awsumeSession.get('Expiration'):
            if awsumeSession['Expiration'].tzinfo != None:
                awsumeSession['Expiration'] = awsumeSession['Expiration'].astimezone(dateutil.tz.tzlocal())
        return awsumeSession
    print >> sys.stderr, '#Error::invalid role'
    exit(1)

def session_string(awsumeSession):
    """
    awsumeSession - the session to create a string out of
    create a formatted string containing
    useful space-delimited credential information
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
    sessionString - the formatted string that contains session credentials
    return a session dict containing those session credentials
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

def write_session(cacheFilePath, cacheFileName, awsumeSession):
    """
    cacheFilePath - the path to write the cache file to
    cacheFileName - the name of the file to write
    awsumeSession - the session to write
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

def read_session(cacheFilePath, cacheFileName):
    """
    cacheFilePath - the path to read from
    cacheFilename - the name of the cache file
    return a session if the path to the file exists
    """
    if os.path.isfile(cacheFilePath + cacheFileName):
        in_file = open(cacheFilePath + cacheFileName, 'r')
        awsumeSession = parse_session_string(in_file.read())
    else:
        awsumeSession = collections.OrderedDict()
    return awsumeSession

def is_valid(awsumeSession):
    """
    awsumeSession - the session to validate
    return whether or not the session is valid,
    if credentials are expired, or don't exist, they're invalid
    else they are valid
    """
    if awsumeSession.get('Expiration'):
        if awsumeSession.get('Expiration') > datetime.datetime.now().replace():
            return True
        print >> sys.stderr, '#Session credentials have expired, refreshing session.'
        return False
    return False

def main():
    #get command-line arguments and handle them
    args = handle_parameters(sys.argv[1:])

    #get config and credentials profiles as dicts
    if args.default is True or args.profile_name == 'default':
        #make sure we always look at the default profile
        args.profile_name = 'default'
        #default profiles aren't prefixed by 'profile '
        configProfile = get_section('default', get_sections(HOME_PATH + '/.aws/config'))
    else:
        configProfile = get_section('profile ' + args.profile_name, get_sections(HOME_PATH + '/.aws/config'))

    if is_role(configProfile):
        #grab the source profile
        credentialsProfile = get_source_profile(configProfile, HOME_PATH + '/.aws/credentials')
    else:
        #the rest of the user, from the credentials file
        credentialsProfile = get_section(args.profile_name, get_sections(HOME_PATH + '/.aws/credentials'))
        if credentialsProfile == collections.OrderedDict():
            print >> sys.stderr, '#Error: Profile not found in credentials file'
            exit(1)

    #if the profile doesn't exist, leave
    if not configProfile and not credentialsProfile:
        print >> sys.stderr, '#Error: Profile [' + args.profile_name + '] not found'
        exit(1)

    #make sure credentials profile is valid
    validate_credentials_profile(credentialsProfile)

    #if the user is AWSuming a user profile, and no mfa is required
    #no more work is required
    if not is_role(configProfile) and 'mfa_serial' not in configProfile:
        print "True " + \
                credentialsProfile.get('aws_secret_access_key') + " " + \
                "None" + " " + \
                credentialsProfile.get('aws_access_key_id') + " " + \
                str(configProfile.get('region')) #region may or may not be 'NoneType'
        exit(0)

    #now we have to get the session token
    #the boto3 client used to make aws calls
    userClient = create_client(credentialsProfile['__name__'])

    #here we check for used credentials
    filePath = HOME_PATH + '/.aws/cli/cache/'
    fileName = 'awsume-temp-' + credentialsProfile['__name__']

    cacheSession = read_session(filePath, fileName)
    if is_valid(cacheSession):
        awsumeUserSession = cacheSession
    #verify the expiration, or if the user wants to force-refresh
    if args.refresh or not is_valid(cacheSession):
        #set the session
        awsUserSession = get_session(userClient, configProfile)
        awsumeUserSession = create_awsume_session(awsUserSession, configProfile)
        write_session(filePath, fileName, awsumeUserSession)

    returnSession = awsumeUserSession
    #at this point we have valid user credentials
    #if we're assuming a role, then we need to call assume_role
    if is_role(configProfile):
        #create new client based on the new session credentials
        roleClient = create_client(None,
                                   awsumeUserSession['SecretAccessKey'],
                                   awsumeUserSession['AccessKeyId'],
                                   awsumeUserSession['SessionToken'])
        awsumeRoleSession = create_awsume_session(assume_role(roleClient,
                                                              configProfile['role_arn'],
                                                              configProfile['__name__'].replace('profile ', '') + '-awsume-session'
                                                             ), configProfile)
        returnSession = awsumeRoleSession
    #send shell script wrapper the session environment variables
    print 'True' + ' ' + session_string(returnSession)

if __name__ == '__main__':
    main()
