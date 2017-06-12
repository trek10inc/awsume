import sys, os, ConfigParser, re, argparse, collections, datetime, dateutil, boto3

#get cross-platform home directory
HOME_PATH = os.path.expanduser('~')

#arguments - a list of arguments
#parse through the arguments
#return a namespace
def handle_parameters(arguments):
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

#iniFile - the file to create a parser out of
#return a dict of sections from the file
def get_sections(iniFile):
    if os.path.exists(iniFile):
        PARSER = ConfigParser.ConfigParser()
        PARSER.read(iniFile)
        return PARSER._sections
    print >> sys.stderr, '#Error::invalid file path'
    exit(1)

#sectionName - the name of a section to get
#sections - the sections to search in
#return the section under the name `sectionName`
def get_section(sectionName, sections):
    #check if profile exists
    if sectionName in sections:
        return sections[sectionName]
    return None

#userProfile - the profile that contains the source profile name
#sourceFilePath - the file that contains the source profile of `userProfile`
#return the source profile of userProfile, if there is no source_profile, return `userProfile` itself
def get_source_profile(userProfile, sourceFilePath):
    if os.path.exists(sourceFilePath):
        if is_role(userProfile):
            return get_section(userProfile['source_profile'], get_sections(sourceFilePath))
        userProfile = userProfile
        userProfile['__name__'] = userProfile['__name__'].replace('profile ', '')
        return userProfile
    print >> sys.stderr, '#Error::invalid file path'
    exit(1)

#profileToCheck - the profile to check
#return if `profileToCheck` is a role or user
def is_role(profileToCheck):
    if 'source_profile' in profileToCheck:
        return True
    return False

#prompt the user to enter an MFA code
#return the string entered by the user
def read_mfa():
    print >> sys.stderr, '#Enter MFA Code:'
    return raw_input()

#mfaToken - the token to validate
#return if `mfaToken` is a valid MFA code
def valid_mfa_token(mfaToken):
    mfaTokenPattern = re.compile('^[0-9]{6}$')
    if not mfaTokenPattern.match(mfaToken):
        return False
    return True

#profileName - the name of the profile to create the client with
#secretAccessKey - secret access key that can be passed into the session
#accessKeyId - access key id that can be passed into the session
#sessionToken - session token that can be passed into the session
#return a boto3 session client
def create_client(profileName=None, secretAccessKey=None, accessKeyId=None, sessionToken=None):
    botoSession = boto3.Session(profile_name=profileName,
                                aws_access_key_id=accessKeyId,
                                aws_secret_access_key=secretAccessKey,
                                aws_session_token=sessionToken)

    return botoSession.client('sts', region_name='us-east-1')

#mfaToken - the MFA code to pass to the sts call
#getSessionTokenClient - the client to make the call on
def get_session(mfaToken, getSessionTokenClient):
    if not valid_mfa_token(mfaToken):
        print >> sys.stderr, '#Invalid MFA Code'
        exit(1)
    #get the mfa serial
    mfaSerial = getSessionTokenClient.get_caller_identity()['Arn'].replace('user', 'mfa')
    return getSessionTokenClient.get_session_token(
        SerialNumber=mfaSerial,
        TokenCode=mfaToken
    )

#assumeRoleClient - the client to make the sts call on
#roleArn - the role arn to use when assuming the role
#roleSessionName - the name to assign to the role-assumed session
#assume role and return the session credentials
def assume_role(assumeRoleClient, roleArn, roleSessionName):
    return assumeRoleClient.assume_role(
        RoleArn=roleArn,
        RoleSessionName=roleSessionName
    )

#awsRole - contains the credentials required for setting the session
#awsProfile - contains the region required for setting the session
#returns a dict of the session to set
def create_awsume_session(awsRole, awsProfile):
    awsumeSession = collections.OrderedDict()
    if awsRole.get('Credentials'):
        awsumeSession['SecretAccessKey'] = awsRole.get('Credentials').get('SecretAccessKey')
        awsumeSession['SessionToken'] = awsRole.get('Credentials').get('SessionToken')
        awsumeSession['AccessKeyId'] = awsRole.get('Credentials').get('AccessKeyId')
        awsumeSession['region'] = awsProfile.get('region')
        awsumeSession['Expiration'] = awsRole.get('Credentials').get('Expiration')
        #convert the time to local time
        if awsumeSession['Expiration'].tzinfo != None:
            awsumeSession['Expiration'] = awsumeSession['Expiration'].astimezone(dateutil.tz.tzlocal())
        return awsumeSession
    print >> sys.stderr, '#Error::invalid role'
    exit(1)

#awsumeSession - the session to create a string out of
#create a formatted string containing
#useful space-delimited credential information
#if an empty session is given, an empty string is returned
def session_string(awsumeSession):
    if all(cred in awsumeSession for cred in ('SecretAccessKey', 'SessionToken', 'AccessKeyId', 'region')):
        return str(awsumeSession['SecretAccessKey']) + ' ' + \
            str(awsumeSession['SessionToken']) + ' ' + \
            str(awsumeSession['AccessKeyId']) + ' ' + \
            str(awsumeSession['region'])
    return ''

#sessionString - the formatted string that contains session credentials
#return a session dict containing those session credentials
def parse_session_string(sessionString):
    sessionArray = sessionString.split(' ')
    awsumeSession = collections.OrderedDict()
    if len(sessionArray) == 5:
        awsumeSession['SecretAccessKey'] = sessionArray[0]
        awsumeSession['SessionToken'] = sessionArray[1]
        awsumeSession['AccessKeyId'] = sessionArray[2]
        awsumeSession['region'] = sessionArray[3]
        awsumeSession['Expiration'] = datetime.datetime.strptime(sessionArray[4], '%Y-%m-%d_%H-%M-%S')
    return awsumeSession

#cacheFilePath - the path to write the cache file to
#cacheFileName - the name of the file to write
#awsumeSession - the session to write
#write the session to the file path
def write_session(cacheFilePath, cacheFileName, awsumeSession):
    if not os.path.exists(cacheFilePath):
        os.makedirs(cacheFilePath)
    out_file = open(cacheFilePath + cacheFileName, 'w+')
    out_file.write(session_string(awsumeSession) + ' ' + awsumeSession['Expiration'].strftime('%Y-%m-%d_%H-%M-%S'))
    out_file.close()

#cacheFilePath - the path to read from
#cacheFilename - the name of the cache file
#return a session if the
def read_session(cacheFilePath, cacheFileName):
    if os.path.isfile(cacheFilePath + cacheFileName):
        in_file = open(cacheFilePath + cacheFileName, 'r')
        awsumeSession = parse_session_string(in_file.read())
    else:
        awsumeSession = collections.OrderedDict()
    return awsumeSession

#awsumeSession - the session to validate
#return whether or not the session is valid,
# if credentials are expired, or don't exist, they're invalid
# else they are valid
def is_valid(awsumeSession):
    if awsumeSession.get('Expiration'):
        if awsumeSession.get('Expiration') > datetime.datetime.now().replace():
            return True
        print >> sys.stderr, '#Session credentials have expired, refreshing session.'
        return False
    return False

if __name__ == '__main__':
    #get command-line arguments and handle them
    args = handle_parameters(sys.argv[1:])
    if args.default is True:
        args.profile_name = 'default'
    #grab the profile dict from the config file
    profile = get_section('profile ' + args.profile_name, get_sections(HOME_PATH + '/.aws/config'))
    #if profile isn't in the config file, check the credentials file
    if not profile:
        profile = get_section(args.profile_name, get_sections(HOME_PATH + '/.aws/credentials'))

    #if the profile doesn't exist, leave
    if not profile:
        print >> sys.stderr, '#Profile [' + args.profile_name + '] not found'
        exit(1)
    sourceProfile = get_source_profile(profile, HOME_PATH + '/.aws/credentials')

    client = create_client(sourceProfile['__name__']) #the boto3 client used to make aws calls

    #here we check for used credentials
    filePath = HOME_PATH + '/.aws/cli/cache/'
    fileName = 'awsume-temp-' + sourceProfile['__name__']
    session = read_session(filePath, fileName)

    #verify the expiration, or if the user wants to force-refresh
    if args.refresh or not is_valid(session):
        #set the session
        userSession = get_session(read_mfa(), client)
        session = create_awsume_session(userSession, profile)

        #write session to cache
        write_session(filePath, fileName, session)

    #create new client based on the new session credentials
    client = create_client(None,
                           session['SecretAccessKey'],
                           session['AccessKeyId'],
                           session['SessionToken'])

    #assume the role if applicable
    if is_role(profile):
        session = create_awsume_session(assume_role(client, profile['role_arn'], profile['__name__'].replace('profile ', '') + '-awsume-session'), profile)

    #send shell script wrapper the session environment variables
    print 'True' + ' ' + session_string(session)
