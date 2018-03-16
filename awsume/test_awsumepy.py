"""Test Awsumepy"""
import datetime
import unittest
import imp
import mock

AWSUMEPY = imp.load_source('awsumepy', 'awsume/awsumepy.py')



#
#   TestCommandLineArgumentHandling
#
class TestCommandLineArgumentHandling(unittest.TestCase):
    """Test suite for CommandLineArgumentHandling"""
    @mock.patch('argparse.ArgumentParser')
    def test_generate_argument_parser(self, mock_arg_parser):
        """test generate_argument_parser awsumepy function"""
        AWSUMEPY.generate_argument_parser()
        mock_arg_parser.assert_called_once()

    def test_add_arguments(self):
        """test add_arguments awsumepy function"""
        mock_add_argument = mock.Mock()
        mock_argument_parser = mock.Mock()
        mock_argument_parser.add_argument = mock_add_argument
        AWSUMEPY.add_arguments(mock_argument_parser)
        mock_add_argument.assert_called()

    def test_parse_args(self):
        """test parse_args awsumepy function"""
        mock_parse_args = mock.Mock()
        mock_argument_parser = mock.Mock()
        mock_argument_parser.parse_args = mock_parse_args
        system_arguments = ['sys', 'args']
        AWSUMEPY.parse_args(mock_argument_parser, system_arguments)
        mock_parse_args.assert_called_with(system_arguments)



#
#   TestReadAWSFiles
#
class TestReadAWSFiles(unittest.TestCase):
    """Test suite for ReadAWSFiles"""
    @mock.patch('six.moves.builtins.print')
    @mock.patch('six.moves.configparser.ConfigParser')
    @mock.patch('os.path.exists')
    def test_read_ini_file(self,
                           mock_path_exists,
                           mock_config_parser,
                           mock_print):
        """test read_ini_file awsumepy function"""
        mock_path_exists.return_value = True
        mock_config_object = mock.Mock()
        mock_config_object.read = mock.Mock()
        mock_config_parser.return_value = mock_config_object
        mock_config_object.sections = mock.Mock()
        mock_config_object.sections.return_value = ['first-profile', 'profile next-profile']
        mock_config_object.options = mock.Mock()
        mock_config_object.options.side_effect = [['key'], ['key2']]
        mock_config_object.get = mock.Mock()
        mock_config_object.get.side_effect = ['value', 'value']
        profiles = AWSUMEPY.read_ini_file('path')
        mock_config_object.read.assert_called_once_with('path')
        self.assertEqual(profiles, {
            'first-profile': {
                '__name__':'first-profile',
                'key':'value'
            },
            'next-profile': {
                '__name__':'next-profile',
                'key2':'value'
            }
        })

        mock_path_exists.return_value = False
        AWSUMEPY.read_ini_file('path')
        mock_print.assert_called_once()

    def test_merge_profile(self):
        """test merge_role_and_source_profile awsumepy function"""
        user_profile = {
            '__name__': 'user_profile',
            'aws_access_key_id':'EXAMPLE',
            'aws_secret_access_key':'EXAMPLE'
        }
        role_profile = {
            '__name__': 'role_profile',
            'source_profile':'EXAMPLE',
            'role_arn':'EXAMPLE'
        }
        AWSUMEPY.merge_role_and_source_profile(role_profile, user_profile)
        self.assertIsNotNone(role_profile.get('aws_access_key_id'))
        self.assertIsNotNone(role_profile.get('aws_secret_access_key'))

        user_profile = {
            '__name__': 'user_profile',
            'aws_access_key_id':'EXAMPLE',
            'aws_secret_access_key':'EXAMPLE',
            'mfa_serial':'EXAMPLE',
            'region':'EXAMPLE',
        }
        role_profile = {
            '__name__': 'role_profile',
            'source_profile':'EXAMPLE',
            'role_arn':'EXAMPLE',
        }
        AWSUMEPY.merge_role_and_source_profile(role_profile, user_profile)
        self.assertIsNotNone(role_profile.get('aws_access_key_id'))
        self.assertIsNotNone(role_profile.get('aws_secret_access_key'))
        self.assertIsNotNone(role_profile.get('mfa_serial'))
        self.assertIsNotNone(role_profile.get('region'))

    @mock.patch('six.moves.builtins.print')
    def test_mix_profiles(self, mock_print):
        """test mix_role_and_source_profiles awsumepy function"""
        fake_profiles = {
            'client-dev-role': {
                '__name__': 'client-dev-role',
                'role_arn': 'EXAMPLE',
                'source_profile': 'client'
            },
            'client': {
                '__name__': 'client',
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE'
            },
            'client-prod-role': {
                '__name__': 'client-prod-role',
                'role_arn': 'EXAMPLE',
                'source_profile': 'client'
            },
        }
        AWSUMEPY.mix_role_and_source_profiles(fake_profiles)
        self.assertIsNotNone(fake_profiles['client-dev-role'].get('aws_access_key_id'))
        self.assertIsNotNone(fake_profiles['client-dev-role'].get('aws_secret_access_key'))
        self.assertIsNotNone(fake_profiles['client-prod-role'].get('aws_access_key_id'))
        self.assertIsNotNone(fake_profiles['client-prod-role'].get('aws_secret_access_key'))

        fake_profiles = {
            'client-dev-role': {
                'role_arn': 'EXAMPLE',
                'source_profile': 'missing-profile'
            },
        }
        with self.assertRaises(SystemExit):
            AWSUMEPY.mix_role_and_source_profiles(fake_profiles)
        mock_print.assert_called()

    @mock.patch('awsumepy.read_ini_file')
    def test_get_aws_profiles(self, mock_read_ini_file):
        """test get_aws_profiles awsumepy function"""
        mock_config_profiles = {
            'client-dev': {
                'key3':'value3',
                'key4':'value4'
            }
        }
        mock_credentials_profiles = {
            'client-dev': {
                'key1':'value1',
                'key2':'value2'
            },
            'auto-refresh-client-dev': {
                'key1':'value1',
                'key2':'value2'
            },
        }
        mock_read_ini_file.side_effect = [mock_config_profiles, mock_credentials_profiles]
        mock_app = None
        mock_arguments = None
        mock_profiles = AWSUMEPY.get_aws_profiles(mock_app, mock_arguments, '/config/path', '/credentials/path')
        self.assertEqual(mock_profiles, {
            'client-dev': {
                'key1':'value1',
                'key2':'value2',
                'key3':'value3',
                'key4':'value4'
            }
        })
        self.assertFalse('auto-refresh-client-dev' in mock_credentials_profiles)

    def test_trim_auto_profiles(self):
        """test trim_auto_profiles awsumepy function"""
        fake_profiles = {
            'auto-refresh-client-profile': {
                'key':'value'
            },
            'client-profile': {
                'key':'value'
            },
            'auto-refresh-internal-profile': {
                'key':'value'
            },
            'internal-profile': {
                'key':'value'
            },
        }
        AWSUMEPY.trim_auto_profiles(fake_profiles)
        self.assertFalse('auto-refresh-client-profile' in fake_profiles)
        self.assertFalse('auto-refresh-internal-profile' in fake_profiles)
        self.assertTrue('internal-profile' in fake_profiles)
        self.assertTrue('client-profile' in fake_profiles)



#
#   TestListingProfiles
#
class TestListingProfiles(unittest.TestCase):
    """Test suite for ListingProfiles"""
    def test_get_account_id(self):
        """test get_account_id awsumepy function"""
        fake_profile_with_role_arn = {
            'role_arn': 'arn:aws:iam::8675309:role/dev-role'
        }
        fake_profile_with_mfa = {
            'mfa_serial': 'arn:aws:iam::123456789012:mfa/admin'
        }
        fake_profile_with_nothing = {
            'aws_access_key_id': 'EXAMPLE',
            'aws_secret_access_key': 'EXAMPLE'
        }
        self.assertEqual(AWSUMEPY.get_account_id(fake_profile_with_mfa), '123456789012')
        self.assertEqual(AWSUMEPY.get_account_id(fake_profile_with_role_arn), '8675309')
        self.assertEqual(AWSUMEPY.get_account_id(fake_profile_with_nothing), 'Unavailable')

    def test_format_aws_profiles(self):
        """test format_aws_profiles awsumepy function"""
        fake_profiles = {
            'client-dev-role': {
                'role_arn': 'EXAMPLE',
                'source_profile': 'client',
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
            },
            'client': {
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
            },
            'client-prod-role': {
                'role_arn': 'EXAMPLE',
                'source_profile': 'client',
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
            },
        }
        fake_profile_list = AWSUMEPY.format_aws_profiles(fake_profiles)
        flattened_list = [item for sublist in fake_profile_list for item in sublist]
        self.assertTrue('client-dev-role' in flattened_list)
        self.assertTrue('client-prod-role' in flattened_list)
        self.assertTrue('client' in flattened_list)
        self.assertTrue('EXAMPLE' in flattened_list)

    @mock.patch('awsumepy.print_formatted_data')
    @mock.patch('awsumepy.format_aws_profiles')
    def test_list_profile_data(self,
                               mock_format_aws_profiles,
                               mock_print_formatted_data):
        """test list_profile_data awsumepy function"""
        AWSUMEPY.list_profile_data({})
        mock_format_aws_profiles.assert_called()
        mock_print_formatted_data.assert_called()

    @mock.patch('awsumepy.mix_role_and_source_profiles')
    @mock.patch('awsumepy.get_aws_profiles')
    def test_get_profile_names(self,
                               mock_get_aws_profiles,
                               mock_mix_profiles):
        """test get_profile_names awsumepy function"""
        fake_profiles = {
            'client-dev-role': {
                'role_arn': 'EXAMPLE',
                'source_profile': 'client',
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
            },
            'client': {
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
            },
            'client-prod-role': {
                'role_arn': 'EXAMPLE',
                'source_profile': 'client',
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
            },
        }
        mock_get_aws_profiles.return_value = fake_profiles
        fake_profile_names = AWSUMEPY.get_profile_names(None, None)
        self.assertTrue('client-dev-role' in fake_profile_names)
        self.assertTrue('client' in fake_profile_names)
        self.assertTrue('client-prod-role' in fake_profile_names)

    @mock.patch('six.moves.builtins.print')
    def test_list_profile_names(self, mock_print):
        """Test list_profile_names awsumepy function"""
        fake_args = mock.Mock()
        fake_app = mock.Mock()
        plugin_func1 = mock.Mock()
        plugin_func1.return_value = [
            'profile1-dev',
            'profile1-prod',
            'profile1-internal',
        ]
        plugin_func2 = mock.Mock()
        plugin_func2.return_value = [
            'profile2-dev',
            'profile2-prod',
            'profile2-internal',
        ]
        fake_app.awsumeFunctions = {
            'get_profile_names':[plugin_func1, plugin_func2]
        }
        AWSUMEPY.list_profile_names(fake_args, fake_app)
        mock_print.assert_called_once_with('profile1-dev\nprofile1-prod\nprofile1-internal\nprofile2-dev\nprofile2-prod\nprofile2-internal')




#
#   TestInspectionAndValidation
#
class TestInspectionAndValidation(unittest.TestCase):
    """Test suite for InspectionAndValidation"""
    @mock.patch('awsumepy.is_role')
    def test_valid_profile(self, mock_is_role):
        """test valid_profile awsumepy function"""
        valid_user = {
            'aws_access_key_id':'EXAMPLE',
            'aws_secret_access_key':'EXAMPLE'
        }
        valid_role = {
            'source_profile':'EXAMPLE',
            'role_arn':'EXAMPLE'
        }
        mock_missing_access_key_id = {
            'aws_secret_access_key':'EXAMPLE'
        }
        mock_missing_secret_access_key = {
            'aws_access_key_id':'EXAMPLE'
        }
        mock_is_role.return_value = True
        self.assertTrue(AWSUMEPY.valid_profile(valid_user))
        self.assertTrue(AWSUMEPY.valid_profile(valid_role))
        mock_is_role.return_value = False
        self.assertFalse(AWSUMEPY.valid_profile(mock_missing_access_key_id))
        self.assertFalse(AWSUMEPY.valid_profile(mock_missing_secret_access_key))

    def test_requires_mfa(self):
        """test requires_mfa awsumepy function"""
        mfa_profile = {
            'aws_access_key_id':'EXAMPLE',
            'aws_secret_access_key':'EXAMPLE',
            'mfa_serial':'EXAMPLE'
        }
        no_mfa_profile = {
            'aws_access_key_id':'EXAMPLE',
            'aws_secret_access_key':'EXAMPLE'
        }
        self.assertTrue(AWSUMEPY.requires_mfa(mfa_profile))
        self.assertFalse(AWSUMEPY.requires_mfa(no_mfa_profile))

    def test_is_role(self):
        """test is_role awsumepy function"""
        user_profile = {
            'aws_access_key_id':'EXAMPLE',
            'aws_secret_access_key':'EXAMPLE',
        }
        role_profile = {
            'source_profile':'EXAMPLE',
            'role_arn':'EXAMPLE'
        }
        self.assertTrue(AWSUMEPY.is_role(role_profile))
        self.assertFalse(AWSUMEPY.is_role(user_profile))

    def test_valid_mfa_token(self):
        """test valid_mfa_token awsumepy function"""
        valid_tokens = [
            '000000',
            '999999',
            '123456'
        ]
        invalid_tokens = [
            '12345',
            '1234567',
            '12345a',
            '      ',
            '',
            'abcdef'
        ]
        for token in valid_tokens:
            self.assertTrue(AWSUMEPY.valid_mfa_token(token))
        for token in invalid_tokens:
            self.assertFalse(AWSUMEPY.valid_mfa_token(token))

    def test_valid_cache_session(self):
        """test valid_cache_session awsumepy function"""
        valid_session = {
            'Expiration': '9999-12-31 11:59:59',
        }
        invalid_session = {

        }
        expired_session = {
            'Expiration': datetime.datetime.min
        }
        self.assertTrue(AWSUMEPY.valid_cache_session(valid_session))
        self.assertFalse(AWSUMEPY.valid_cache_session(expired_session))
        self.assertFalse(AWSUMEPY.valid_cache_session(invalid_session))

    def test_fix_session_credentials(self):
        """test fix_session_credentials awsumepy function"""
        mock_as_timezone = mock.Mock()
        fake_profiles = {
            'default':{
                'aws_access_key_id':'EXAMPLE',
                'aws_secret_access_key':'EXAMPLE',
                'mfa_serial':'EXAMPLE',
                'region':'DefaultRegion'
            },
            'client':{
                'aws_access_key_id':'EXAMPLE',
                'aws_secret_access_key':'EXAMPLE',
            }
        }
        fake_session = {
            'Expiration':mock.Mock()
        }
        fake_args = mock.Mock()
        fake_args.target_profile_name = 'client'
        fake_session['Expiration'].astimezone = mock_as_timezone

        AWSUMEPY.fix_session_credentials(fake_session, fake_profiles, fake_args)
        self.assertTrue(fake_session['region'] == 'DefaultRegion')

        fake_profiles['client']['region'] = 'ClientRegion'
        AWSUMEPY.fix_session_credentials(fake_session, fake_profiles, fake_args)
        self.assertTrue(fake_session['region'] == 'ClientRegion')
        mock_as_timezone.assert_called()



#
#   TestInputOutput
#
class TestInputOutput(unittest.TestCase):
    """Test suite for InputOutput"""
    @mock.patch('awsumepy.valid_mfa_token')
    @mock.patch('awsumepy.get_input')
    def test_read_mfa(self, mock_input, mock_valid_mfa_token):
        """test read_mfa awsumepy function"""
        mock_valid_mfa_token.side_effect = [
            False,
            False,
            False,
            True
        ]
        mock_input.side_effect = [
            'invalid',
            'invalid',
            'invalid',
            'validmfa'
        ]
        token = AWSUMEPY.read_mfa()
        self.assertEqual(token, 'validmfa')



#
#   TestCachingSessions
#
class TestCachingSessions(unittest.TestCase):
    """Test suite for CachingSessions"""
    @mock.patch('six.moves.builtins.open')
    @mock.patch('json.load')
    @mock.patch('os.path.isfile')
    def test_read_aws_cache(self,
                            mock_os_path_isfile,
                            mock_json_load,
                            mock_open):
        """test read_aws_cache awsumepy function"""
        mock_os_path_isfile.return_value = True
        mock_json_load.return_value = {'Expiration': '1999-12-31 11:59:59'}
        session = AWSUMEPY.read_aws_cache('/cache/path/', 'cache-file')
        self.assertEqual(session, {
            'Expiration': '1999-12-31 11:59:59'
        })
        mock_os_path_isfile.return_value = False
        session = AWSUMEPY.read_aws_cache('/cache/path/', 'cache-file')
        self.assertEqual(session, {})

        mock_os_path_isfile.return_value = True
        mock_open.side_effect = Exception
        session = AWSUMEPY.read_aws_cache('/cache/path/', 'cache-file')
        self.assertEqual(session, {})

    @mock.patch('os.makedirs')
    @mock.patch('os.path.exists')
    @mock.patch('six.moves.builtins.open')
    @mock.patch('json.dump')
    def test_write_aws_cache(self,
                             mock_json_dump,
                             mock_open,
                             mock_path_exists,
                             mock_makedirs):
        """test write_aws_cache awsumepy function"""
        mock_path_exists.return_value = True
        AWSUMEPY.write_aws_cache('/cache/path/', 'cache-file', {'session':'credentials'})
        mock_json_dump.assert_called()

        mock_path_exists.return_value = False
        AWSUMEPY.write_aws_cache('/cache/path/', 'cache-file', {'session':'credentials'})
        mock_makedirs.assert_called()



#
#   TestAwsumeWorkflow
#
class TestAwsumeWorkflow(unittest.TestCase):
    """Test suite for AwsumeWorkflow"""
    @mock.patch('awsumepy.display_plugin_info')
    @mock.patch('awsumepy.delete_plugin')
    @mock.patch('awsumepy.download_plugin')
    @mock.patch('awsumepy.list_profile_names')
    @mock.patch('awsumepy.kill')
    def test_pre_awsume(self,
                        mock_kill,
                        mock_list_profile_names,
                        mock_download_plugin,
                        mock_delete_plugin,
                        mock_display_plugin_info):
        """test pre_awsume awsumepy function"""
        fake_args = mock.Mock()
        fake_app = mock.Mock()
        fake_args.version = False
        fake_args.profile_name = None
        fake_args.target_profile_name = None
        fake_args.kill = False
        fake_args.list_profile_names = False
        fake_args.plugin_urls = None
        fake_args.delete_plugin_name = None
        fake_args.display_plugin_info = False
        fake_args.info = False
        fake_args.debug = False

        AWSUMEPY.pre_awsume(fake_app, fake_args)
        self.assertEqual(fake_args.target_profile_name, 'default')

        fake_args.profile_name = 'superCoolClient'
        AWSUMEPY.pre_awsume(fake_app, fake_args)

        self.assertEqual(fake_args.target_profile_name, 'superCoolClient')
        fake_args.profile_name = None

        fake_args.kill = True
        with self.assertRaises(SystemExit):
            AWSUMEPY.pre_awsume(fake_app, fake_args)

        mock_kill.assert_called_once()
        fake_args.kill = False

        fake_args.list_profile_names = True
        with self.assertRaises(SystemExit):
            AWSUMEPY.pre_awsume(fake_app, fake_args)

        mock_list_profile_names.assert_called_once()
        fake_args.list_profile_names = False

        fake_args.plugin_urls = ['url1', 'url2']
        with self.assertRaises(SystemExit):
            AWSUMEPY.pre_awsume(fake_app, fake_args)

        mock_download_plugin.assert_called_once()
        fake_args.plugin_urls = None

        fake_args.delete_plugin_name = 'somePlugin'
        with self.assertRaises(SystemExit):
            AWSUMEPY.pre_awsume(fake_app, fake_args)

        mock_delete_plugin.assert_called_once()
        fake_args.delete_plugin_name = None

        fake_args.display_plugin_info = True
        with self.assertRaises(SystemExit):
            AWSUMEPY.pre_awsume(fake_app, fake_args)

        mock_display_plugin_info.assert_called_once()
        fake_args.display_plugin_info = False

    @mock.patch('boto3.client')
    def test_create_sts_client(self, mock_client):
        """test create_sts_client awsumepy function"""
        AWSUMEPY.create_sts_client()
        self.assertTrue('sts' in args for args in mock_client.call_args_list)

    @mock.patch('awsumepy.fix_session_credentials')
    @mock.patch('awsumepy.read_mfa')
    @mock.patch('awsumepy.requires_mfa')
    @mock.patch('awsumepy.create_sts_client')
    @mock.patch('awsumepy.is_role')
    @mock.patch('awsumepy.read_aws_cache')
    @mock.patch('awsumepy.write_aws_cache')
    @mock.patch('awsumepy.valid_cache_session')
    def test_get_user_session(self,
                              mock_valid_cache_session,
                              mock_write_cache,
                              mock_read_aws_cache,
                              mock_is_role,
                              mock_create_sts_client,
                              mock_requires_mfa,
                              mock_read_mfa,
                              mock_fix_session_credentials):
        """test get_user_session awsumepy function"""
        mock_get_session_token = mock.Mock()
        mock_get_session_token.return_value = {'Credentials': {'SessionToken':'EXAMPLE'}}
        mock_client = mock.Mock()
        mock_client.get_session_token = mock_get_session_token
        mock_create_sts_client.return_value = mock_client
        fake_app = mock.Mock()
        fake_args = mock.Mock()
        fake_profiles = {
            'fake-nomfa-user': {
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE'
            },
            'fake-mfa-profile': {
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
                'mfa_serial': 'EXAMPLE'
            },
            'fake-role-profile': {
                'source_profile': 'fake-mfa-profile',
                'role_arn': 'EXAMPLE',
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
                'mfa_serial': 'EXAMPLE'
            }
        }

        fake_args.target_profile_name = 'fake-nomfa-user'
        mock_requires_mfa.return_value = False
        mock_is_role.return_value = False
        fake_args.force_refresh = False
        fake_session = AWSUMEPY.get_user_session(fake_app, fake_args, fake_profiles, '/cache/path', None)
        self.assertEqual(fake_session, {
            'AccessKeyId' : 'EXAMPLE',
            'SecretAccessKey' : 'EXAMPLE',
            'region' : None,
        })

        fake_args.target_profile_name = 'fake-mfa-profile'
        mock_requires_mfa.return_value = True
        mock_is_role.return_value = False
        fake_args.force_refresh = False
        mock_valid_cache_session.return_value = True
        mock_read_aws_cache.return_value = 'fake_session'
        fake_session = AWSUMEPY.get_user_session(fake_app, fake_args, fake_profiles, '/cache/path', None)
        self.assertEqual(fake_session, 'fake_session')

        fake_args.target_profile_name = 'fake-mfa-profile'
        mock_requires_mfa.return_value = True
        mock_is_role.return_value = False
        fake_args.force_refresh = True
        mock_valid_cache_session.return_value = False
        fake_session = AWSUMEPY.get_user_session(fake_app, fake_args, fake_profiles, '/cache/path', None)
        self.assertEqual(fake_session, {
            'SessionToken':'EXAMPLE'
        })

        fake_args.target_profile_name = 'fake-role-profile'
        mock_requires_mfa.return_value = False
        mock_is_role.return_value = True
        fake_args.force_refresh = True
        mock_valid_cache_session.return_value = False
        fake_session = AWSUMEPY.get_user_session(fake_app, fake_args, fake_profiles, '/cache/path', None)
        self.assertEqual(fake_session, {
            'SessionToken':'EXAMPLE'
        })

    @mock.patch('awsumepy.fix_session_credentials')
    @mock.patch('awsumepy.create_sts_client')
    def test_get_role_session(self,
                              mock_create_sts_client,
                              mock_fix_session_credentials):
        """test get_role_session awsumepy function"""
        fake_app = mock.Mock()
        fake_args = mock.Mock()
        fake_args.session_name = None
        fake_args.target_profile_name = 'default'
        mock_assume_role = mock.Mock()
        mock_client = mock.Mock()
        mock_client.assume_role = mock_assume_role
        mock_create_sts_client.return_value = mock_client
        fake_profiles = {
            'fake-nomfa-user': {
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE'
            },
            'fake-mfa-profile': {
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
                'mfa_serial': 'EXAMPLE'
            },
            'fake-role-profile': {
                'source_profile': 'fake-mfa-profile',
                'role_arn': 'EXAMPLE',
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
                'mfa_serial': 'EXAMPLE'
            }
        }
        fake_user_session = {
            'AccessKeyId':'EXAMPLE',
            'SecretAccessKey':'EXAMPLE',
            'SessionToken':'EXAMPLE'
        }

        fake_args.target_profile_name = 'fake-role-profile'
        mock_assume_role.return_value = {
            'Credentials': {
                'SessionToken':'EXAMPLE'
            }
        }
        session = AWSUMEPY.get_role_session(fake_app, fake_args, fake_profiles, fake_user_session, None)
        self.assertEqual(session, {'SessionToken':'EXAMPLE'})
        mock_assume_role.assert_called_with(RoleArn='EXAMPLE', RoleSessionName='awsume-session-fake-role-profile')

        fake_args.session_name = 'cool-session'
        session = AWSUMEPY.get_role_session(fake_app, fake_args, fake_profiles, fake_user_session, None)
        self.assertEqual(session, {'SessionToken':'EXAMPLE'})
        mock_assume_role.assert_called_with(RoleArn='EXAMPLE', RoleSessionName='cool-session')



#
#   TestAutoAwsume
#
class TestAutoAwsume(unittest.TestCase):
    """Test suite for autoawsume"""
    @mock.patch('awsumepy.kill_all_auto_processes')
    @mock.patch('awsumepy.write_auto_awsume_session')
    @mock.patch('awsumepy.create_auto_profile')
    def test_start_auto_awsume(self,
                               mock_create_auto_profile,
                               mock_write_auto_awsume_session,
                               mock_kill_all_auto_processes):
        """test start_auto_awsume awsumepy function"""
        fake_args = mock.Mock()
        fake_app = mock.Mock()
        fake_app.set_export_data = mock.Mock()
        fake_user_session = {}
        fake_role_session = {}
        fake_profiles = {
            'fake-nomfa-user': {
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE'
            },
            'fake-mfa-profile': {
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
                'mfa_serial': 'EXAMPLE'
            },
            'fake-role-profile': {
                'source_profile': 'fake-mfa-profile',
                'role_arn': 'EXAMPLE',
                'aws_access_key_id': 'EXAMPLE',
                'aws_secret_access_key': 'EXAMPLE',
                'mfa_serial': 'EXAMPLE'
            }
        }

        fake_args.target_profile_name = 'fake-role-profile'
        fake_args.session_name = None
        AWSUMEPY.start_auto_awsume(fake_args, fake_app, fake_profiles, '/creds/path', fake_user_session, fake_role_session)
        fake_app.set_export_data.assert_called_with({'AWSUME_FLAG':'Auto', 'AWSUME_LIST':[
            'auto-refresh-fake-role-profile',
            'fake-role-profile'
        ]})

        fake_args.target_profile_name = 'fake-role-profile'
        fake_args.session_name = 'custom-session-name'
        AWSUMEPY.start_auto_awsume(fake_args, fake_app, fake_profiles, '/creds/path', fake_user_session, fake_role_session)
        self.assertTrue(mock.call({}, {}, 'custom-session-name', 'fake-mfa-profile', 'EXAMPLE') in mock_create_auto_profile.call_args_list)

    @mock.patch('six.moves.configparser.ConfigParser')
    def test_is_auto_profiles(self,
                              mock_config_parser):
        """test is_auto_profiles awsumepy function"""
        mock_config_object = mock.Mock()
        mock_config_parser.return_value = mock_config_object
        mock_config_object.read = mock.Mock()
        mock_config_object.sections = mock.Mock()
        mock_config_object.sections.return_value = ['auto-refresh-profile']
        self.assertTrue(AWSUMEPY.is_auto_profiles('/cred/path/'))
        mock_config_object.sections.return_value = ['profile']
        self.assertFalse(AWSUMEPY.is_auto_profiles('/cred/path/'))

    @mock.patch('six.moves.builtins.open')
    @mock.patch('six.moves.configparser.ConfigParser')
    def test_remove_auto_profile(self,
                                 mock_config_parser,
                                 mock_open):
        """test remove_auto_profile awsumepy function"""
        mock_config_object = mock.Mock()
        mock_config_parser.return_value = mock_config_object
        mock_config_object.read = mock.Mock()
        mock_config_object.write = mock.Mock()
        mock_config_object.sections = mock.Mock()
        mock_config_object.has_section = mock.Mock()
        mock_config_object.remove_section = mock.Mock()

        profile_name = 'some-profile'
        mock_config_object.has_section.return_value = False
        AWSUMEPY.remove_auto_profile(profile_name)
        mock_config_object.remove_section.assert_not_called()

        mock_config_object.has_section.return_value = True
        mock_config_object.sections.return_value = [
            'auto-refresh-profile-1',
            'auto-refresh-profile-2',
            'normal-profile-3',
        ]
        AWSUMEPY.remove_auto_profile(profile_name)
        mock_config_object.remove_section.assert_called()

        profile_name = None
        AWSUMEPY.remove_auto_profile(profile_name)
        self.assertEqual(mock_config_object.remove_section.call_count, 3)

    @mock.patch('six.moves.builtins.open')
    @mock.patch('six.moves.configparser.ConfigParser')
    def test_write_auto_awsume_session(self,
                                       mock_config_parser,
                                       mock_open):
        """test write_auto_awsume_session awsumepy function"""
        mock_config_object = mock.Mock()
        mock_config_object.read = mock.Mock()
        mock_config_object.write = mock.Mock()
        mock_config_object.has_section = mock.Mock()
        mock_config_object.remove_section = mock.Mock()
        mock_config_object.add_section = mock.Mock()
        mock_config_parser.return_value = mock_config_object
        mock_config_object.sections = mock.Mock()

        mock_config_object.sections.return_value = [
            'auto-refresh-profile-1',
            'auto-refresh-profile-2',
            'normal-profile-3',
        ]
        profile_name = 'client-dev'
        fake_auto_profile = {
            'key': 'value'
        }
        mock_config_object.has_section.return_value = True
        AWSUMEPY.write_auto_awsume_session(profile_name, fake_auto_profile, '/cred/path')
        mock_config_object.read.assert_called()
        mock_config_object.remove_section.assert_called()
        mock_config_object.write.assert_called()

    def test_create_auto_profile(self):
        """test create_auto_profile awsumepy function"""
        fake_role_session = {
            'AccessKeyId':'EXAMPLE',
            'SecretAccessKey':'EXAMPLE',
            'SessionToken':'EXAMPLE',
            'region':'EXAMPLE',
            'Expiration':'EXAMPLE',
        }
        fake_user_session = {
            'Expiration':'EXAMPLE'
        }
        fake_session_name = 'cool-session'
        fake_source_profile_name = 'client-source'
        fake_role_arn = 'EXAMPLE'
        auto_profile = AWSUMEPY.create_auto_profile(fake_role_session, fake_user_session, fake_session_name, fake_source_profile_name, fake_role_arn)
        self.assertEqual(auto_profile, {
            'aws_access_key_id' : 'EXAMPLE',
            'aws_secret_access_key' : 'EXAMPLE',
            'aws_session_token' : 'EXAMPLE',
            'aws_region' : 'EXAMPLE',
            'awsume_role_expiration' : 'EXAMPLE',
            'awsume_user_expiration' : 'EXAMPLE',
            'awsume_session_name' : 'cool-session',
            'awsume_cache_name' : 'awsume-credentials-client-source',
            'aws_role_arn' : 'EXAMPLE'
        })

    @mock.patch('psutil.process_iter')
    def test_kill_all_auto_processes(self, mock_process_iter):
        """test kill_all_auto_processes awsumepy function"""
        proc1 = mock.Mock()
        proc1.kill = mock.Mock()
        proc1.cmdline = mock.Mock()
        proc1.cmdline.return_value = ['bash']
        proc2 = mock.Mock()
        proc2.kill = mock.Mock()
        proc2.cmdline = mock.Mock()
        proc2.cmdline.return_value = ['autoawsume']
        proc3 = mock.Mock()
        proc3.kill = mock.Mock()
        proc3.cmdline = mock.Mock()
        proc3.cmdline.return_value = ['otherProgram']
        mock_process_iter.return_value = [proc1, proc2, proc3]

        AWSUMEPY.kill_all_auto_processes()
        proc1.kill.assert_not_called()
        proc2.kill.assert_called()
        proc3.kill.assert_not_called()

        proc2.kill.side_effect = Exception
        AWSUMEPY.kill_all_auto_processes()

    @mock.patch('awsumepy.kill_all_auto_processes')
    @mock.patch('awsumepy.is_auto_profiles')
    @mock.patch('awsumepy.remove_auto_profile')
    def test_kill(self,
                  mock_remove_auto_profile,
                  mock_is_auto_profiles,
                  mock_kill_all_auto_processes):
        """Test kill awsumepy function"""
        fake_args = mock.Mock()
        fake_app = mock.Mock()
        fake_app.set_export_data = mock.Mock()
        fake_app.export_data = mock.Mock()

        fake_args.profile_name = None
        AWSUMEPY.kill(fake_args, fake_app)
        mock_kill_all_auto_processes.assert_called_once()
        mock_remove_auto_profile.assert_called_once_with()
        fake_app.set_export_data.assert_called_once()
        fake_app.export_data.assert_called_once()

        fake_args.profile_name = 'some-profile'
        mock_is_auto_profiles.return_value = True
        AWSUMEPY.kill(fake_args, fake_app)
        self.assertEqual(mock_kill_all_auto_processes.call_count, 1)
        mock_remove_auto_profile.assert_called_with('some-profile')
        self.assertEqual(fake_app.set_export_data.call_count, 2)
        self.assertEqual(fake_app.export_data.call_count, 2)

        fake_args.profile_name = 'some-profile'
        mock_is_auto_profiles.return_value = False
        AWSUMEPY.kill(fake_args, fake_app)
        self.assertEqual(mock_kill_all_auto_processes.call_count, 2)
        mock_remove_auto_profile.assert_called_with('some-profile')
        self.assertEqual(fake_app.set_export_data.call_count, 3)
        self.assertEqual(fake_app.export_data.call_count, 3)



#
#   TestPluginManagement
#
class TestPluginManagement(unittest.TestCase):
    """Test suite for Plugin Manaement"""
    def test_get_main_content_type(self):
        python2_http_message_object = mock.Mock(spec=[])
        python2_http_message_object.getmaintype = mock.Mock()
        python2_http_message_object.getmaintype.return_value = 'Python2MainType'
        python3_http_message_object = mock.Mock(spec=[])
        python3_http_message_object.getmaintype = mock.Mock()
        python3_http_message_object.getmaintype.return_value = 'Python3MainType'

        python2_type = AWSUMEPY.get_main_content_type(python2_http_message_object)
        self.assertEqual(python2_type, 'Python2MainType')
        python3_type = AWSUMEPY.get_main_content_type(python3_http_message_object)
        self.assertEqual(python3_type, 'Python3MainType')

    @mock.patch('awsumepy.get_main_content_type')
    @mock.patch('six.moves.urllib.request.urlopen')
    @mock.patch('six.moves.configparser.ConfigParser')
    def test_download_file(self, mock_config_parser, mock_urlopen, mock_get_content_type):
        """Test download_file awsumepy function"""
        mock_response = mock.Mock()
        mock_response.info = mock.Mock()
        mock_response.read = mock.Mock()
        mock_response.read.return_value = b'plugin file contents'
        mock_urlopen.return_value = mock_response

        mock_get_content_type.return_value = 'text'
        fake_file = AWSUMEPY.download_file('fake-url')
        self.assertEqual(fake_file, 'plugin file contents')

        mock_get_content_type.return_value = 'video'
        with self.assertRaises(Exception):
            fake_file = AWSUMEPY.download_file('fake-url')

    @mock.patch('six.moves.builtins.open')
    @mock.patch('awsumepy.get_input')
    @mock.patch('os.path.isfile')
    def test_write_plugin_files(self,
                                mock_isfile,
                                mock_input,
                                mock_open):
        """Test write_plugin_files awsumepy function"""
        fake_file1 = 'python file contents'
        fake_file2 = 'yapsy-plugin file contents'
        fake_filename1 = 'plugin.py'
        fake_filename2 = 'plugin.yapsy-plugin'

        mock_isfile.return_value = True
        mock_input.return_value = 'n'
        AWSUMEPY.write_plugin_files(fake_file1, fake_file2, fake_filename1, fake_filename2)
        mock_open.assert_not_called()

        mock_isfile.return_value = True
        mock_input.return_value = 'y'
        AWSUMEPY.write_plugin_files(fake_file1, fake_file2, fake_filename1, fake_filename2)
        self.assertEqual(mock_open.call_count, 2)

        mock_isfile.return_value = False
        mock_input.return_value = ''
        AWSUMEPY.write_plugin_files(fake_file1, fake_file2, fake_filename1, fake_filename2)
        self.assertEqual(mock_open.call_count, 4)

    @mock.patch('awsumepy.read_plugin_cache')
    @mock.patch('awsumepy.cache_urls')
    @mock.patch('awsumepy.write_plugin_files')
    @mock.patch('awsumepy.download_file')
    def test_download_plugin(self,
                             mock_download_file,
                             mock_write_plugin_files,
                             mock_cache_urls,
                             mock_read_plugin_cache):
        """Test download_plugin awsumepy function"""
        fake_url1 = 'https://website.com/invalid/'
        fake_url2 = 'https://website.com/invalid/'
        AWSUMEPY.download_plugin(fake_url1, fake_url2)
        mock_download_file.assert_not_called()
        mock_write_plugin_files.assert_not_called()

        fake_url1 = 'https://website.com/invalid/wrongFile.txt'
        fake_url2 = 'https://website.com/invalid/wrongFile.jpg'
        AWSUMEPY.download_plugin(fake_url1, fake_url2)
        mock_download_file.assert_not_called()
        mock_write_plugin_files.assert_not_called()

        fake_url1 = 'https://website.com/valid/plugin.py'
        fake_url2 = 'https://website.com/valid/plugin.yapsy-plugin'
        AWSUMEPY.download_plugin(fake_url1, fake_url2)
        self.assertEqual(mock_download_file.call_count, 2)
        mock_write_plugin_files.assert_called()

        fake_url1 = 'plugin.py'
        fake_url2 = 'plugin.yapsy-plugin'
        mock_read_plugin_cache.return_value = {
            'plugin.py':'url1',
            'plugin.yapsy-plugin':'url2'
        }
        AWSUMEPY.download_plugin(fake_url1, fake_url2)
        self.assertEqual(mock_download_file.call_count, 4)
        mock_read_plugin_cache.assert_called()
        self.assertEqual(mock_write_plugin_files.call_count, 2)

        mock_download_file.side_effect = Exception
        AWSUMEPY.download_plugin(fake_url1, fake_url2)
        self.assertEqual(mock_write_plugin_files.call_count, 2)

    @mock.patch('awsumepy.get_input')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.isfile')
    @mock.patch('os.path.join')
    @mock.patch('shutil.rmtree')
    @mock.patch('os.remove')
    @mock.patch('os.listdir')
    def test_delete_plugin(self,
                           mock_ls,
                           mock_rm,
                           mock_rmtree,
                           mock_join,
                           mock_isfile,
                           mock_isdir,
                           mock_input):
        """Test delete_plugin awsumepy function"""
        fake_plugin_name = 'somePlugin'
        mock_ls.return_value = [
            'otherPlugin.py',
            'otherPlugin.yapsy-plugin',
        ]
        AWSUMEPY.delete_plugin(fake_plugin_name)
        mock_rm.assert_not_called()
        mock_rmtree.assert_not_called()

        mock_ls.return_value = [
            'somePlugin.py',
            'somePlugin.yapsy-plugin',
            'otherPlugin.py',
            'otherPlugin.yapsy-plugin',
        ]
        mock_input.return_value = 'n'
        AWSUMEPY.delete_plugin(fake_plugin_name)
        mock_rm.assert_not_called()
        mock_rmtree.assert_not_called()

        mock_isfile.side_effect = [True, False]
        mock_isdir.side_effect = [True]
        mock_input.return_value = 'y'
        AWSUMEPY.delete_plugin(fake_plugin_name)
        mock_rm.assert_called_once()
        mock_rmtree.assert_called_once()

    @mock.patch('six.moves.builtins.open')
    @mock.patch('json.load')
    @mock.patch('os.path.isfile')
    def test_read_plugin_cache(self, mock_isfile, mock_load, mock_open):
        """Test read_plugin_cache awsumepy function"""
        mock_isfile.return_value = True
        mock_load.return_value = {'plugin.py':'url'}
        cache = AWSUMEPY.read_plugin_cache()
        self.assertEqual(cache, {'plugin.py':'url'})
        mock_open.assert_called()

        mock_isfile.return_value = False
        self.assertEqual(AWSUMEPY.read_plugin_cache(), {})

    @mock.patch('six.moves.builtins.open')
    @mock.patch('json.dump')
    @mock.patch('awsumepy.read_plugin_cache')
    def test_cache_urls(self, mock_read_plugin_cache, mock_dump, mock_open):
        """Test cache_urls awsumepy function"""
        mock_read_plugin_cache.return_value = {
            'plugin.py':'url',
            'plugin.yapsy-plugin':'url',
        }
        AWSUMEPY.cache_urls('url', 'url', 'otherPlugin.py', 'otherPlugin.yapsy-plugin')
        target_cache = {
            'plugin.py':'url',
            'plugin.yapsy-plugin':'url',
            'otherPlugin.py':'url',
            'otherPlugin.yapsy-plugin':'url',
        }
        args, _ = mock_dump.call_args_list[0]
        self.assertTrue(target_cache in args)



#
#   TestAwsumeApp
#
class TestAwsumeApp(unittest.TestCase):
    """Test suite for AwsumeApp"""
    @mock.patch('awsumepy.PluginManager')
    def test_create_plugin_manager(self, mock_plugin_manager):
        """test create_plugin_manager awsumepy function"""
        mock_manager = mock.Mock()
        mock_manager.setPluginPlaces = mock.Mock()
        mock_manager.collectPlugins = mock.Mock()
        mock_plugin_manager.PluginManager = mock.Mock()
        mock_plugin_manager.PluginManager.return_value = mock_manager

        manager = AWSUMEPY.create_plugin_manager('/dir')
        mock_manager.setPluginPlaces.assert_called_once_with(['/dir'])
        mock_manager.collectPlugins.assert_called_once()
        self.assertEqual(manager, mock_manager)

        mock_manager.collectPlugins.side_effect = [Exception]
        manager = AWSUMEPY.create_plugin_manager('/dir')
        self.assertEqual(manager, None)

    def test_register_plugins(self):
        """test register_plugins awsumepy function"""
        AWSUMEPY.__version__ = '0.0.0'

        fake_app = mock.Mock()
        fake_app.register_function = mock.Mock()
        fake_app.validFunctions = ['fn1', 'fn2']

        plugin1 = mock.Mock()
        plugin1.name = 'plugin1'
        plugin1.plugin_object = mock.Mock()
        plugin1.plugin_object.TARGET_VERSION = '0.0.0'
        plugin1.plugin_object.fn1 = mock.Mock()
        plugin1.plugin_object.fn2 = mock.Mock()

        plugin2 = mock.Mock()
        plugin2.name = 'plugin2'
        plugin2.plugin_object = mock.Mock()
        plugin2.plugin_object.TARGET_VERSION = '0.0.0'
        plugin2.plugin_object.fn1 = mock.Mock()
        plugin2.plugin_object.fn2 = mock.Mock()

        fake_manager = mock.Mock()
        fake_manager.getAllPlugins = mock.Mock()
        fake_manager.getAllPlugins.return_value = [plugin1, plugin2]

        AWSUMEPY.register_plugins(fake_app, fake_manager)
        self.assertEqual(fake_app.register_function.call_count, 4)

        AWSUMEPY.__version__ = '1.0.0'
        AWSUMEPY.register_plugins(fake_app, fake_manager)
        self.assertEqual(fake_app.register_function.call_count, 8)

        plugin2.plugin_object.TARGET_VERSION = mock.Mock(spec=[])
        AWSUMEPY.register_plugins(fake_app, fake_manager)
        self.assertEqual(fake_app.register_function.call_count, 12)

        plugin2.plugin_object.TARGET_VERSION = '0.0.0'
        fake_app.register_function.return_value = False
        AWSUMEPY.register_plugins(fake_app, fake_manager)
        self.assertEqual(fake_app.register_function.call_count, 16)


if __name__ == '__main__':
    unittest.main()
