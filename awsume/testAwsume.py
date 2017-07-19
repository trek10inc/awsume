import sys
import unittest
import collections
import datetime
import argparse
import awsumepy

    #parse_arguments
    #handle_command_line_arguments
    #get_profiles_from_ini_file
    #get_ini_profile_by_name
    #get_config_profile
    #get_credentials_profile
    #validate_profiles
    #handle_profiles
#get_awsume_user_credentials
#get_awsume_role_credentials
#start_auto_refresher
#handle_getting_role_credentials
    #validate_credentials_profile
    #get_source_profile_from_role
    #is_role_profile
#read_mfa
    #is_valid_mfa_token
#create_boto_sts_client
#get_session_token_credentials
#get_assume_role_credentials
    #create_awsume_session
    #session_string
    #parse_session_string
#write_awsume_session_to_file
    #read_awsume_session_from_file
    #is_valid_awsume_session
#write_auto_awsume_session
#kill_all_auto_processes
#remove_all_auto_profiles
#remove_auto_awsume_profile_by_name
#is_auto_refresh_profiles
#stop_auto_refresh
#generate_formatted_data
#print_formatted_data
#list_profile_data


#
#   Testing for awsume methods that awsumepy.handle input and input validation
#

class TestInput(unittest.TestCase):
    version_args = None
    list_profile_args = None
    kill_args = None
    default_args = None
    default_profile_args = None

    def create_empty_namesapce(self):
        arg_namespace = argparse.Namespace()
        arg_namespace.profile_name = 'default'
        arg_namespace.default = False
        arg_namespace.show = False
        arg_namespace.refresh = False
        arg_namespace.auto_refresh = False
        arg_namespace.kill = False
        arg_namespace.version = False
        arg_namespace.list_profiles = False
        return arg_namespace

    def setUp(self):
        self.version_args = self.create_empty_namesapce()
        self.version_args.version = True
        self.list_profile_args = self.create_empty_namesapce()
        self.list_profile_args.list_profiles = True
        self.kill_args = self.create_empty_namesapce()
        self.kill_args.kill = True
        self.default_args = self.create_empty_namesapce()
        self.default_args.default = True
        self.default_profile_args = self.create_empty_namesapce()

    def test_parse_arguments(self):
        #normal use-cases
        self.assertTrue(awsumepy.parse_arguments(['-d', '-r', '-s']).refresh)
        self.assertTrue(awsumepy.parse_arguments(['-d', '-r', '-s']).show)
        self.assertTrue(awsumepy.parse_arguments(['-d', '-r', '-s']).default)
        self.assertEqual(awsumepy.parse_arguments(['input_name']).profile_name, 'input_name')
        #unrecognized inputs will stop the script
        with self.assertRaises(SystemExit) as cm:
            awsumepy.parse_arguments(['one_name', 'two_name'])
        self.assertEqual(cm.exception.code, 2)

    def test_is_valid_mfa_token(self):
        #normal use-cases
        self.assertTrue(awsumepy.is_valid_mfa_token('123456'))
        #incorrect mfa tokens
        self.assertFalse(awsumepy.is_valid_mfa_token(''))
        self.assertFalse(awsumepy.is_valid_mfa_token('12345'))
        self.assertFalse(awsumepy.is_valid_mfa_token('1234567'))
        self.assertFalse(awsumepy.is_valid_mfa_token('abcdef'))
        self.assertFalse(awsumepy.is_valid_mfa_token('abc123'))
        self.assertFalse(awsumepy.is_valid_mfa_token('a23456'))
        self.assertFalse(awsumepy.is_valid_mfa_token('12345*'))

    def test_handle_command_line_arguments(self):
        #version flag on
        with self.assertRaises(SystemExit) as cm:
            awsumepy.handle_command_line_arguments(self.version_args)
        self.assertEqual(cm.exception.code, 0)
        #list_profiles flag on
        with self.assertRaises(SystemExit) as cm:
            awsumepy.handle_command_line_arguments(self.list_profile_args)
        self.assertEqual(cm.exception.code, 0)
        #kill flag on
        with self.assertRaises(SystemExit) as cm:
            awsumepy.handle_command_line_arguments(self.kill_args)
        self.assertEqual(cm.exception.code, 0)
        #default flag on
        awsumepy.handle_command_line_arguments(self.default_args)
        self.assertTrue(self.default_args.default)
        self.assertEqual(self.default_args.profile_name, 'default')
        #no profile name given
        awsumepy.handle_command_line_arguments(self.default_profile_args)
        self.assertTrue(self.default_profile_args.default)
        self.assertEqual(self.default_profile_args.profile_name, 'default')


#
#   Testing for awsume methods that handle reading sections from config or credential INI files
#

class TestINISectionMethods(unittest.TestCase):
    expected_example_sections = collections.OrderedDict()

    def setUp(self):
        self.expected_example_sections['default'] = collections.OrderedDict()
        self.expected_example_sections['profile user-profile'] = collections.OrderedDict()
        self.expected_example_sections['profile no-mfa-user'] = collections.OrderedDict()
        self.expected_example_sections['profile role-profile'] = collections.OrderedDict()

        self.expected_example_sections['default']['__name__'] = 'default'
        self.expected_example_sections['default']['region'] = 'us-east-1'
        self.expected_example_sections['default']['mfa_serial'] = 'mfaSERIAL'
        self.expected_example_sections['profile user-profile']['__name__'] = 'profile user-profile'
        self.expected_example_sections['profile user-profile']['mfa_serial'] = 'mfaSERIAL'
        self.expected_example_sections['profile user-profile']['region'] = 'us-west-2'
        self.expected_example_sections['profile no-mfa-user']['__name__'] = 'profile no-mfa-user'
        self.expected_example_sections['profile no-mfa-user']['region'] = 'us-east-2'
        self.expected_example_sections['profile role-profile']['__name__'] = 'profile role-profile'
        self.expected_example_sections['profile role-profile']['source_profile'] = 'role_source'
        self.expected_example_sections['profile role-profile']['role_arn'] = 'ROLEarn'

    def test_get_profiles_from_ini_file(self):
        #normal use-cases
        self.assertEqual(awsumepy.get_profiles_from_ini_file('./test/example'), self.expected_example_sections)
        #getting sections from an empty file
        self.assertEqual(awsumepy.get_profiles_from_ini_file('./test/emptyFile'), collections.OrderedDict())
        #getting sections from a file that doesn't exist
        with self.assertRaises(SystemExit) as cm:
            awsumepy.get_profiles_from_ini_file('./test/a/path/that/does/not/exist')
        self.assertEqual(cm.exception.code, 1)

    def test_get_ini_profile_by_name(self):
        #normal use case
        self.assertEqual(awsumepy.get_ini_profile_by_name('default', self.expected_example_sections), self.expected_example_sections['default'])
        self.assertEqual(awsumepy.get_ini_profile_by_name('profile user-profile', self.expected_example_sections), self.expected_example_sections['profile user-profile'])
        self.assertEqual(awsumepy.get_ini_profile_by_name('profile role-profile', self.expected_example_sections), self.expected_example_sections['profile role-profile'])
        #getting a section that doesn't exist in the sections
        self.assertEqual(awsumepy.get_ini_profile_by_name('non-existent-profile', self.expected_example_sections), collections.OrderedDict())

    def test_is_auto_refresh_profiles(self):
        #an auto-awsume profile is there
        self.assertFalse(awsumepy.is_auto_refresh_profiles())

#
#   Testing for awsume methods that handle profiles
#

class TestProfileMethods(unittest.TestCase):
    example_default_profile = collections.OrderedDict()
    example_role_profile = collections.OrderedDict()
    example_user_profile = collections.OrderedDict()
    example_user_no_mfa_profile = collections.OrderedDict()
    example_no_credentials_profile = collections.OrderedDict()
    expected_no_mfa_user_credentials_profile = collections.OrderedDict()

    expected_source_profile = collections.OrderedDict()
    expected_user_credentials_profile = collections.OrderedDict()
    no_access_key_id_user_profile = collections.OrderedDict()
    no_secret_access_key_user_profile = collections.OrderedDict()

    default_args = argparse.Namespace()
    role_profile_args = argparse.Namespace()
    user_profile_args = argparse.Namespace()
    no_credentials_profile_args = argparse.Namespace()

    def setUp(self):
        self.example_default_profile['__name__'] = 'default'
        self.example_default_profile['region'] = 'us-east-1'
        self.example_default_profile['mfa_serial'] = 'mfaSERIAL'
        self.example_role_profile['__name__'] = 'profile role-profile'
        self.example_role_profile['source_profile'] = 'role_source'
        self.example_role_profile['role_arn'] = 'ROLEarn'
        self.example_user_profile['__name__'] = 'profile user-profile'
        self.example_user_profile['mfa_serial'] = 'mfaSERIAL'
        self.example_user_profile['region'] = 'us-west-2'
        self.example_user_no_mfa_profile['__name__'] = 'no-mfa-user'
        self.example_user_no_mfa_profile['region'] = 'us-east-2'
        self.example_no_credentials_profile['__name__'] = 'no_credentials_profile'
        self.example_no_credentials_profile['region'] = 'us-west-1'

        self.expected_source_profile['__name__'] = 'role_source'
        self.expected_source_profile['aws_access_key_id'] = 'ACCESSkeyID'
        self.expected_source_profile['aws_secret_access_key'] = 'SECRETaccessKEY'
        self.expected_user_credentials_profile['__name__'] = 'user-profile'
        self.expected_user_credentials_profile['aws_access_key_id'] = 'ACCESSkeyID'
        self.expected_user_credentials_profile['aws_secret_access_key'] = 'SECRETaccessKEY'
        self.expected_no_mfa_user_credentials_profile['__name__'] = 'user-profile'
        self.expected_no_mfa_user_credentials_profile['aws_access_key_id'] = 'ACCESSkeyID'
        self.expected_no_mfa_user_credentials_profile['aws_secret_access_key'] = 'SECRETaccessKEY'
        self.no_access_key_id_user_profile['__name__'] = 'noaki'
        self.no_access_key_id_user_profile['aws_secret_access_key_id'] = 'SECRETaccessKEY'
        self.no_secret_access_key_user_profile['__name__'] = 'nosak'
        self.no_secret_access_key_user_profile['aws_access_key_id'] = 'ACCESSkeyID'

        self.default_args.default = True
        self.role_profile_args.default = False
        self.user_profile_args.default = False
        self.no_credentials_profile_args.default = False
        self.role_profile_args.profile_name = 'role-profile'
        self.user_profile_args.profile_name = 'user-profile'
        self.no_credentials_profile_args.profile_name = 'no_credentials_file'

        #set the config file
        awsumepy.AWS_CONFIG_FILE = './test/example'
        awsumepy.AWS_CREDENTIALS_FILE = './test/exampleCredentials'

    def tearDown(self):
        awsumepy.AWS_CONFIG_FILE = awsumepy.HOME_PATH + '/.aws/config'
        awsumepy.AWS_CREDENTIALS_FILE = awsumepy.HOME_PATH + '/.aws/credentials'

    def test_get_source_profile_from_role(self):
        #normal use-cases
        self.assertEqual(awsumepy.get_source_profile_from_role(self.example_role_profile, './test/exampleCredentials'), self.expected_source_profile)

        #if we try getting the source profile of a non-role profile, it'll return an empty dict
        self.assertEqual(awsumepy.get_source_profile_from_role(self.example_user_profile, './test/exampleCredentials'), collections.OrderedDict())

    def test_is_role_profile(self):
        #normal use-cases
        self.assertTrue(awsumepy.is_role_profile(self.example_role_profile))
        self.assertFalse(awsumepy.is_role_profile(self.expected_source_profile))

    def test_validate_credentials_profile(self):
        with self.assertRaises(SystemExit) as cm:
            #a user profile missing their secret access key
            awsumepy.validate_credentials_profile(self.no_secret_access_key_user_profile)
        self.assertEqual(cm.exception.code, 1)

        with self.assertRaises(SystemExit) as cm:
            #a user profile missing their access key id
            awsumepy.validate_credentials_profile(self.no_access_key_id_user_profile)
        self.assertEqual(cm.exception.code, 1)

        with self.assertRaises(SystemExit) as cm:
            #a user profile missing both access keys, or a role
            awsumepy.validate_credentials_profile(self.example_role_profile)
        self.assertEqual(cm.exception.code, 1)

    def test_get_config_profile(self):
        #normal use-cases
        self.assertEqual(awsumepy.get_config_profile(self.default_args), self.example_default_profile)
        self.assertEqual(awsumepy.get_config_profile(self.role_profile_args), self.example_role_profile)
        self.assertEqual(awsumepy.get_config_profile(self.user_profile_args), self.example_user_profile)

    def test_get_credentials_profile(self):
        #normal use-cases
        self.assertEqual(awsumepy.get_credentials_profile(self.example_role_profile, self.role_profile_args), self.expected_source_profile)
        self.assertEqual(awsumepy.get_credentials_profile(self.example_user_profile, self.user_profile_args), self.expected_user_credentials_profile)
        #no credentials profile for given profile
        with self.assertRaises(SystemExit) as cm:
            awsumepy.get_credentials_profile(self.example_no_credentials_profile, self.no_credentials_profile_args)
        self.assertEqual(cm.exception.code, 1)

    def test_validate_profiles(self):
        #normal use-cases
        with self.assertRaises(SystemExit) as cm:
            awsumepy.validate_profiles(collections.OrderedDict(), collections.OrderedDict())
        self.assertEqual(cm.exception.code, 1)

        with self.assertRaises(SystemExit) as cm:
            awsumepy.validate_profiles(collections.OrderedDict(), self.no_access_key_id_user_profile)
        self.assertEqual(cm.exception.code, 1)

        with self.assertRaises(SystemExit) as cm:
            awsumepy.validate_profiles(collections.OrderedDict(), self.no_secret_access_key_user_profile)
        self.assertEqual(cm.exception.code, 1)

        self.assertIsNone(awsumepy.validate_profiles(self.example_user_profile, self.expected_user_credentials_profile))

    def test_handle_profiles(self):
        #if the profile is a user profile and doesn't require mfa
        with self.assertRaises(SystemExit) as cm:
            awsumepy.handle_profiles(self.example_user_no_mfa_profile, self.expected_no_mfa_user_credentials_profile)
        self.assertEqual(cm.exception.code, 0)

#
#   Testing for awsume methods that handle sessions
#

class TestSessionMethods(unittest.TestCase):
    expected_valid_session = collections.OrderedDict()
    invalid_session = collections.OrderedDict()
    expired_session = collections.OrderedDict()
    empty_session = collections.OrderedDict()

    session_role = collections.OrderedDict()
    session_role['Credentials'] = collections.OrderedDict()
    session_profile = collections.OrderedDict()
    invalid_session_role = collections.OrderedDict()
    invalid_session_profile = collections.OrderedDict()

    expected_session_string = ''

    def setUp(self):
        self.expected_valid_session['SecretAccessKey'] = 'EXAMPLESECRETACCESSKEY'
        self.expected_valid_session['SessionToken'] = 'EXAMPLESESSIONTOKEN'
        self.expected_valid_session['AccessKeyId'] = 'EXAMPLEACCESSKEYID'
        self.expected_valid_session['region'] = 'us-east-1'
        self.expected_valid_session['Expiration'] = datetime.datetime(9999, 12, 31, 23, 59, 59)

        self.invalid_session['SecretAccessKey'] = 'EXAMPLESECRETACCESSKEY'
        self.invalid_session['SessionToken'] = 'EXAMPLESESSIONTOKEN'
        self.invalid_session['AccessKeyId'] = 'EXAMPLEACCESSKEYID'
        self.invalid_session['region'] = 'us-east-1'

        self.expired_session['SecretAccessKey'] = 'EXAMPLESECRETACCESSKEY'
        self.expired_session['SessionToken'] = 'EXAMPLESESSIONTOKEN'
        self.expired_session['AccessKeyId'] = 'EXAMPLEACCESSKEYID'
        self.expired_session['region'] = 'us-east-1'
        self.expired_session['Expiration'] = datetime.datetime.min

        self.session_role['Credentials']['SecretAccessKey'] = 'EXAMPLESECRETACCESSKEY'
        self.session_role['Credentials']['SessionToken'] = 'EXAMPLESESSIONTOKEN'
        self.session_role['Credentials']['AccessKeyId'] = 'EXAMPLEACCESSKEYID'
        self.session_role['Credentials']['Expiration'] = datetime.datetime(9999, 12, 31, 23, 59, 59)
        self.session_profile['region'] = 'us-east-1'

        self.expected_session_string = "EXAMPLESECRETACCESSKEY EXAMPLESESSIONTOKEN EXAMPLEACCESSKEYID us-east-1 9999-12-31_23-59-59"

    def test_is_valid_awsume_session(self):
        #normal use-cases
        self.assertTrue(awsumepy.is_valid_awsume_session(self.expected_valid_session))
        #testing an empty sessin
        self.assertFalse(awsumepy.is_valid_awsume_session(self.empty_session))
        self.assertFalse(awsumepy.is_valid_awsume_session(self.expired_session))
        self.assertFalse(awsumepy.is_valid_awsume_session(self.invalid_session))

    def test_session_string(self):
        #normal use-cases
        self.assertEqual(awsumepy.session_string(self.expected_valid_session),
                         self.expected_valid_session['SecretAccessKey'] + ' ' + \
                         self.expected_valid_session['SessionToken'] + ' ' + \
                         self.expected_valid_session['AccessKeyId'] + ' ' + \
                         self.expected_valid_session['region'])
        #converting an empty session to a string
        self.assertEqual(awsumepy.session_string(self.empty_session), '')

    def test_create_awsume_session(self):
        #normal use-cases
        self.assertEqual(awsumepy.create_awsume_session(self.session_role, self.session_profile), self.expected_valid_session)
        #passing an invalid role and profile will exit the script
        with self.assertRaises(SystemExit) as cm:
            awsumepy.create_awsume_session(self.invalid_session_role, self.invalid_session_profile)
        self.assertEqual(cm.exception.code, 1)

    def test_parse_session_string(self):
        #normal use-cases
        self.assertEqual(awsumepy.parse_session_string(self.expected_session_string), self.expected_valid_session)
        #passing an empty string
        self.assertEqual(awsumepy.parse_session_string(''), collections.OrderedDict())
        #passing an incompatible string (missing region)
        self.assertEqual(awsumepy.parse_session_string('secretaccesskey sessiontoken accesskeyid 9999-12-31_23-59-59'), collections.OrderedDict())
        #passing an incompatible string (an extra value)
        self.assertEqual(awsumepy.parse_session_string('secretaccesskey sessiontoken accesskeyid us-east-1 9999-12-31_23-59-59 extraValue'), collections.OrderedDict())

    def test_read_awsume_session_from_file(self):
        #normal use-cases
        self.assertEqual(awsumepy.read_awsume_session_from_file("./test/", "exampleSession"), self.expected_valid_session)
        #passing a non-existent file
        self.assertEqual(awsumepy.read_awsume_session_from_file("/non/existant/path", "non-existent-file"), collections.OrderedDict())
        #passing an empty file
        self.assertEqual(awsumepy.read_awsume_session_from_file("./test/", "emptyFile"), collections.OrderedDict())






if __name__ == '__main__':
    unittest.main()
