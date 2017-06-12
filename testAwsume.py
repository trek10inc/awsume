import unittest
import collections
import datetime
import awsume

#
#   Testing for awsume methods that handle input and input validation
#

class TestInput(unittest.TestCase):
    def test_handle_parameters(self):
        #normal use-cases
        self.assertTrue(awsume.handle_parameters(['-d', '-r', '-s']).refresh)
        self.assertTrue(awsume.handle_parameters(['-d', '-r', '-s']).show)
        self.assertTrue(awsume.handle_parameters(['-d', '-r', '-s']).default)
        self.assertEqual(awsume.handle_parameters(['-d']).profile_name, 'default')
        self.assertEqual(awsume.handle_parameters(['input_name']).profile_name, 'input_name')
        #possibly misleading inputs
        self.assertEqual(awsume.handle_parameters([]).profile_name, 'default')
        #unrecognized inputs will stop the script
        with self.assertRaises(SystemExit):
            awsume.handle_parameters(['one_name', 'two_name'])

    def test_valid_mfa_token(self):
        #normal use-cases
        self.assertTrue(awsume.valid_mfa_token('123456'))
        #incorrect mfa tokens
        self.assertFalse(awsume.valid_mfa_token(''))
        self.assertFalse(awsume.valid_mfa_token('12345'))
        self.assertFalse(awsume.valid_mfa_token('1234567'))
        self.assertFalse(awsume.valid_mfa_token('abcdef'))
        self.assertFalse(awsume.valid_mfa_token('abc123'))
        self.assertFalse(awsume.valid_mfa_token('a23456'))
        self.assertFalse(awsume.valid_mfa_token('12345*'))

#
#   Testing for awsume methods that handle reading sections from config or credential INI files
#

class TestINISectionMethods(unittest.TestCase):
    expected_example_sections = collections.OrderedDict()
    expected_example_sections['profile hello'] = collections.OrderedDict()
    expected_example_sections['profile hasSource'] = collections.OrderedDict()
    expected_example_section_hello = collections.OrderedDict()
    expected_example_section_hasSource = collections.OrderedDict()

    def setUp(self):
        self.expected_example_sections['profile hello']['__name__'] = 'profile hello'
        self.expected_example_sections['profile hello']['key1'] = 'value1'
        self.expected_example_sections['profile hello']['key2'] = 'value2'
        self.expected_example_sections['profile hasSource']['__name__'] = 'profile hasSource'
        self.expected_example_sections['profile hasSource']['source_profile'] = 'source'

        self.expected_example_section_hello['__name__'] = 'profile hello'
        self.expected_example_section_hello['key1'] = 'value1'
        self.expected_example_section_hello['key2'] = 'value2'

        self.expected_example_section_hasSource['__name__'] = 'profile hasSource'
        self.expected_example_section_hasSource['source_profile'] = 'source'

    def test_get_sections(self):
        #normal use-cases
        self.assertEqual(awsume.get_sections('./testFiles/example'), self.expected_example_sections)
        #getting sections from an empty file
        self.assertEqual(awsume.get_sections('./testFiles/emptyFile'), collections.OrderedDict())
        #getting sections from a file that doesn't exist
        with self.assertRaises(SystemExit):
            awsume.get_sections('./testFiles/a/path/that/does/not/exist')

    def test_get_section(self):
        #normal use case
        self.assertEqual(awsume.get_section('profile hello', self.expected_example_sections), self.expected_example_section_hello)
        self.assertEqual(awsume.get_section('profile hasSource', self.expected_example_sections), self.expected_example_section_hasSource)
        #getting a section that doesn't exist in the sections
        self.assertIsNone(awsume.get_section('non-existent-profile', self.expected_example_sections))

#
#   Testing for awsume methods that handle profiles
#

class TestProfileMethods(unittest.TestCase):
    example_role_profile = collections.OrderedDict()
    example_user_profile = collections.OrderedDict()
    expected_source_profile = collections.OrderedDict()

    def setUp(self):
        self.example_role_profile['__name__'] = 'profile hasSource'
        self.example_role_profile['source_profile'] = 'role_source'
        self.example_user_profile['__name__'] = 'profile notARole'
        self.example_user_profile['key1'] = 'value1'
        self.expected_source_profile['__name__'] = 'role_source'
        self.expected_source_profile['test'] = 'iAmSource'

    def test_get_source_profile(self):
        #normal use-cases
        self.assertEqual(awsume.get_source_profile(self.example_role_profile, './testFiles/exampleCredentials'), self.expected_source_profile)
        self.assertEqual(awsume.get_source_profile(self.example_user_profile, './testFiles/exampleCredentials'), self.example_user_profile)

    def test_is_role(self):
        #normal use-cases
        self.assertTrue(awsume.is_role(self.example_role_profile))
        self.assertFalse(awsume.is_role(self.expected_source_profile))

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

    def test_is_valid(self):
        #normal use-cases
        self.assertTrue(awsume.is_valid(self.expected_valid_session))
        #testing an empty sessin
        self.assertFalse(awsume.is_valid(self.empty_session))
        self.assertFalse(awsume.is_valid(self.expired_session))
        self.assertFalse(awsume.is_valid(self.invalid_session))

    def test_session_string(self):
        #normal use-cases
        self.assertEqual(awsume.session_string(self.expected_valid_session),
                         self.expected_valid_session['SecretAccessKey'] + ' ' + \
                         self.expected_valid_session['SessionToken'] + ' ' + \
                         self.expected_valid_session['AccessKeyId'] + ' ' + \
                         self.expected_valid_session['region'])
        #converting an empty session to a string
        self.assertEqual(awsume.session_string(self.empty_session), '')

    def test_create_awsume_session(self):
        #normal use-cases
        self.assertEqual(awsume.create_awsume_session(self.session_role, self.session_profile), self.expected_valid_session)
        #passing an invalid role and profile will exit the script
        with self.assertRaises(SystemExit):
            awsume.create_awsume_session(self.invalid_session_role, self.invalid_session_profile)

    def test_parse_session_string(self):
        #normal use-cases
        self.assertEqual(awsume.parse_session_string(self.expected_session_string), self.expected_valid_session)
        #passing an empty string
        self.assertEqual(awsume.parse_session_string(''), collections.OrderedDict())
        #passing an incompatible string (missing region)
        self.assertEqual(awsume.parse_session_string('secretaccesskey sessiontoken accesskeyid 9999-12-31_23-59-59'), collections.OrderedDict())
        #passing an incompatible string (an extra value)
        self.assertEqual(awsume.parse_session_string('secretaccesskey sessiontoken accesskeyid us-east-1 9999-12-31_23-59-59 extraValue'), collections.OrderedDict())

    def test_read_session(self):
        #normal use-cases
        self.assertEqual(awsume.read_session("./testFiles/", "exampleSession"), self.expected_valid_session)
        #passing a non-existent file
        self.assertEqual(awsume.read_session("/non/existant/path", "non-existent-file"), collections.OrderedDict())
        #passing an empty file
        self.assertEqual(awsume.read_session("./testFiles/", "emptyFile"), collections.OrderedDict())



if __name__ == '__main__':
    unittest.main()
