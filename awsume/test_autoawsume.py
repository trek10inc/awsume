"""Test autoawsume"""
import unittest
import sys
import os
import datetime
import imp
import mock
import botocore

sys.path.append(os.path.dirname(sys.path[0]))

AUTOAWSUME = imp.load_source('autoawsume', 'awsume/autoawsume.py')

class TestCommandLineArgumentHandling(unittest.TestCase):

    @mock.patch('awsume.awsumepy.write_auto_awsume_session')
    @mock.patch('awsume.awsumepy.create_sts_client')
    @mock.patch('awsume.awsumepy.read_aws_cache')
    def test_refresh_session(self,
                             mock_read_cache,
                             mock_create_client,
                             mock_write_auto_session):
        """Test the refresh_session autoawsume function"""
        mock_client = mock.Mock()
        mock_client.assume_role = mock.Mock()
        fake_response = {
            'Credentials': {
                'Expiration': mock.Mock(),
                'AccessKeyId':'EXAMPLE',
                'SecretAccessKey':'EXAMPLE',
                'SessionToken':'EXAMPLE',
            }
        }
        mock_client.assume_role.return_value = fake_response
        mock_create_client.return_value = mock_client
        fake_auto_profile = {
            '__name__':'EXAMPLE',
            'aws_access_key_id':'EXAMPLE',
            'aws_secret_access_key':'EXAMPLE',
            'aws_session_token':'EXAMPLE',
            'awsume_role_expiration':'EXAMPLE',
            'awsume_user_expiration':'EXAMPLE',
            'awsume_session_name':'EXAMPLE',
            'awsume_cache_name':'EXAMPLE',
            'aws_role_arn':'EXAMPLE',
        }
        fake_cache_credentials = {
            'AccessKeyId':'EXAMPLE',
            'SecretAccessKey':'EXAMPLE',
            'SessionToken':'EXAMPLE',
            'region':'EXAMPLE',
        }
        mock_read_cache.return_value = fake_cache_credentials
        AUTOAWSUME.refresh_session(fake_auto_profile)
        mock_write_auto_session.assert_called_once()

        mock_client.assume_role.side_effect = [botocore.exceptions.ClientError({}, {})]
        AUTOAWSUME.refresh_session(fake_auto_profile)

    def test_extract_auto_refresh_profiles(self):
        """Test the extract_auto_refresh_profiles autoawsume function"""
        fake_profiles = {
            'some-profile': {},
            'some-other-profile': {},
            'auto-refresh-some-profile': {},
            'auto-refresh-some-other-profile': {},
        }
        auto_profiles = AUTOAWSUME.extract_auto_refresh_profiles(fake_profiles)
        self.assertEqual(auto_profiles, {
            'auto-refresh-some-profile': {},
            'auto-refresh-some-other-profile': {},
        })

    @mock.patch('autoawsume.get_now')
    def test_get_earliest_expiration(self, mock_now):
        """Test the get_earliest_expiration autoawsume function"""
        mock_now.return_value = 'current time'
        fake_auto_profiles = {}
        earliest_expiration = AUTOAWSUME.get_earliest_expiration(fake_auto_profiles)
        self.assertEqual('current time', earliest_expiration)

        fake_auto_profiles = {
            'profile1': {
                'awsume_user_expiration':'2018-06-15 12:24:38',
                'awsume_role_expiration':'2018-06-15 12:24:15',
            },
            'profile2': {
                'awsume_user_expiration':'2018-06-15 12:24:20',
                'awsume_role_expiration':'2018-06-15 12:24:17',
            },
            'profile3': {
                'awsume_user_expiration':'2018-06-15 12:24:02',
                'awsume_role_expiration':'2018-06-15 12:24:54',
            },
        }
        earliest_expiration = AUTOAWSUME.get_earliest_expiration(fake_auto_profiles)
        self.assertEqual(
            datetime.datetime.strptime('2018-06-15 12:24:02', '%Y-%m-%d %H:%M:%S'),
            earliest_expiration)

    @mock.patch('awsume.awsumepy.remove_auto_profile')
    @mock.patch('autoawsume.refresh_session')
    @mock.patch('autoawsume.get_now')
    def test_refresh_expired_profiles(self,
                                      mock_now,
                                      mock_refresh,
                                      mock_remove):
        """Test the refresh_expired_profiles autoawsume function"""
        mock_now.return_value = datetime.datetime.strptime(
            '2018-06-15 12:24:30',
            '%Y-%m-%d %H:%M:%S'
        )
        fake_auto_profiles = {
            'profile1': {
                '__name__':'profile1',
                'awsume_user_expiration':'2018-06-15 12:24:59',#Good
                'awsume_role_expiration':'2018-06-15 12:24:59',#Good
            },
            'profile2': {
                '__name__':'profile2',
                'awsume_user_expiration':'2018-06-15 12:24:00',#Expired
                'awsume_role_expiration':'2018-06-15 12:24:59',#Good
            },
            'profile3': {
                '__name__':'profile3',
                'awsume_user_expiration':'2018-06-15 12:24:59',#Good
                'awsume_role_expiration':'2018-06-15 12:24:00',#Expired
            },
        }
        AUTOAWSUME.refresh_expired_profiles(fake_auto_profiles)
        mock_refresh.assert_called_once()
        mock_remove.assert_called_once()

    @mock.patch('time.sleep')
    @mock.patch('autoawsume.get_now')
    @mock.patch('autoawsume.get_earliest_expiration')
    @mock.patch('autoawsume.refresh_expired_profiles')
    @mock.patch('autoawsume.extract_auto_refresh_profiles')
    @mock.patch('awsume.awsumepy.read_ini_file')
    def test_main(self,
                  mock_read_ini_file,
                  mock_extract_auto_profiles,
                  mock_refresh,
                  mock_get_earliest_expiration,
                  mock_now,
                  mock_sleep):
        """Test the main autoawsume function"""
        mock_read_ini_file.return_value = {}
        mock_extract_auto_profiles.return_value = {}
        mock_get_earliest_expiration.return_value = datetime.datetime(2018, 6, 15, 12, 24, 30)
        mock_now.side_effect = [
            datetime.datetime(2018, 6, 15, 12, 24, 0),
            datetime.datetime(2018, 6, 15, 12, 24, 30),
        ]
        AUTOAWSUME.main()
        mock_sleep.assert_called_once_with(30)

if __name__ == '__main__':
    unittest.main()
