from __future__ import print_function
import sys
import os
import json
import webbrowser
import urllib
import requests

from yapsy import IPlugin
from awsume import awsumepy

# Python 3 compatibility (python 3 has urlencode in parse sub-module)
URLENCODE = getattr(urllib, 'parse', urllib).urlencode

class AwsumeConsole(IPlugin.IPlugin):
    """The AWS Management Console plugin. Opens an assumed-role to the AWS management console."""
    TARGET_VERSION = '3.0.0'

    def add_arguments(self, argument_parser):
        """Add the console flag."""
        argument_parser.add_argument('-c', '--console',
                                     action='store_true',
                                     default=False,
                                     dest='open_console',
                                     help='Open the AWS console to the AWSume\'d credentials')
        return argument_parser

    def pre_awsume(self, app, args):
        """If no profile_name is given to AWSume, check the environment for credentials."""
        #use the environment variables to open
        if args.open_console is True and args.profile_name is None:
            credentials, region = self.get_environment_credentials()
            response = self.make_aws_federation_request(credentials)
            signin_token = self.get_signin_token(response)
            console_url = self.get_console_url(signin_token, region)
            self.open_browser_to_url(console_url)
            exit(0)

    def post_awsume(self,
                    app,
                    args,
                    profiles,
                    user_session,
                    role_session):
        """Open the console using the currently AWSume'd credentials."""
        if args.open_console is True:
            if not role_session:
                awsumepy.safe_print('Cannot use these credentials to open the AWS Console.')
                return
            credentials, region = self.get_session_temp_credentials(role_session)
            response = self.make_aws_federation_request(credentials)
            signin_token = self.get_signin_token(response)
            console_url = self.get_console_url(signin_token, region)
            self.open_browser_to_url(console_url)

    def get_environment_credentials(self):
        """Get session credentials from the environment."""
        aws_region = 'us-east-1'
        if 'AWS_PROFILE' in os.environ:
            credentials_profiles = awsumepy.read_ini_file(awsumepy.AWS_CREDENTIALS_FILE)
            auto_profile = credentials_profiles[os.environ['AWS_PROFILE']]
            temp_credentials = {
                'sessionId': auto_profile['aws_access_key_id'],
                'sessionKey': auto_profile['aws_secret_access_key'],
                'sessionToken': auto_profile['aws_session_token']
            }
            if auto_profile.get('aws_region'):
                aws_region = auto_profile.get('aws_region')
        elif os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY') and os.environ.get('AWS_SESSION_TOKEN'):
            temp_credentials = {
                'sessionId': os.environ['AWS_ACCESS_KEY_ID'],
                'sessionKey': os.environ['AWS_SECRET_ACCESS_KEY'],
                'sessionToken': os.environ['AWS_SESSION_TOKEN']
            }
            if os.environ.get('AWS_REGION'):
                aws_region = os.environ['AWS_REGION']
        else:
            awsumepy.safe_print('Cannot use these credentials to open the AWS Console.')
            exit(0)
        json_temp_credentials = json.dumps(temp_credentials)
        return json_temp_credentials, aws_region

    def get_session_temp_credentials(self, session):
        """Create a properly formatted json string of the given session. Return the session and the region to use."""
        if session.get('AccessKeyId') and session.get('SecretAccessKey') and session.get('SessionToken'):
            aws_region = 'us-east-1'
            temp_credentials = {
                'sessionId': session['AccessKeyId'],
                'sessionKey': session['SecretAccessKey'],
            }
            if 'SessionToken' in session:
                temp_credentials['sessionToken'] = session['SessionToken']
            if session.get('region'):
                aws_region = session['region']

            #format the credentials into a json formatted string
            json_temp_credentials = json.dumps(temp_credentials)
            return json_temp_credentials, aws_region
        awsumepy.safe_print('Cannot use these credentials to open the AWS Console.')
        exit(0)

    def make_aws_federation_request(self, temp_credentials):
        """Make the AWS federation request to get the signin token."""
        params = {
            'Action': 'getSigninToken',
            'Session': temp_credentials,
        }
        request_url = 'https://signin.aws.amazon.com/federation'
        response = requests.get(request_url, params=params)
        return response

    def get_signin_token(self, aws_response):
        """Get the signin token from the aws federation response."""
        return json.loads(aws_response.text)['SigninToken']

    def get_console_url(self, aws_signin_token, aws_region):
        """Get the url to open the browser to."""
        params = {
            'Action': 'login',
            'Issuer': '',
            'Destination': 'https://console.aws.amazon.com/console/home?region=' + aws_region,
            'SigninToken': aws_signin_token
        }
        url = 'https://signin.aws.amazon.com/federation?'
        url += URLENCODE(params)
        return url

    def open_browser_to_url(self, url):
        """Open the default browser to the given url. If that fails, display the url."""
        try:
            webbrowser.open(url)
        except Exception:
            awsumepy.safe_print('Cannot open browser, here is the link:')
            awsumepy.safe_print(url)
