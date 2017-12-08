from __future__ import print_function
import sys, os, json, requests, webbrowser, urllib

from yapsy import IPlugin
from awsume import awsumepy

# Python 3 compatibility (python 3 has urlencode in parse sub-module)
urlencode = getattr(urllib, 'parse', urllib).urlencode

class AwsumeConsole(IPlugin.IPlugin):
    TARGET_VERSION = '2.0.0'

    def add_arguments_func(self, parser):
        #console flag
        parser.add_argument('-c', action='store_true', default='False',
                            dest='open_console',
                            help='Open the AWS console to the AWSume\'d credentials')
        return parser

    def handle_arguments_func(self, arguments, app, out_data):
        #use the environment variables to open
        if arguments.open_console is True and arguments.profile_name is None:
            credentials, region = self.get_temp_credentials_from_environment()
            r = self.make_aws_federation_request(credentials)
            signinToken = self.get_signin_token(r)
            consoleURL = self.get_console_url(signinToken, region)
            self.open_browser_to_url(consoleURL)
            exit(0)

    def post_awsume_func(self,
                         configProfileList,
                         credentialsProfileList,
                         configProfile,
                         credentialsProfile,
                         sessionToUse,
                         arguments,
                         out_data):
        if arguments.open_console is True:
            credentials, region = self.get_temp_credentials_from_session(sessionToUse)
            r = self.make_aws_federation_request(credentials)
            signinToken = self.get_signin_token(r)
            consoleURL = self.get_console_url(signinToken, region)
            self.open_browser_to_url(consoleURL)

    def get_temp_credentials_from_environment(self):
        #We're looking at an auto-awsume'd profile
        awsRegion = 'us-east-1' #default region

        if 'AWS_PROFILE' in os.environ:
            autoProfile = awsumepy.get_ini_profile_by_name(os.environ['AWS_PROFILE'], awsumepy.get_profiles_from_ini_file(awsumepy.AWS_CREDENTIALS_FILE))
            temporaryCredentials = {
                "sessionId": autoProfile['aws_access_key_id'],
                "sessionKey": autoProfile['aws_secret_access_key'],
                "sessionToken": autoProfile['aws_session_token']
            }
            if autoProfile.get('region'):
                awsRegion = autoProfile.get('region')
        #We're looking at a normal awsume'd profile
        elif os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY') and os.environ.get('AWS_SESSION_TOKEN'):
            temporaryCredentials = {
                "sessionId": os.environ['AWS_ACCESS_KEY_ID'],
                "sessionKey": os.environ['AWS_SECRET_ACCESS_KEY'],
                "sessionToken": os.environ["AWS_SESSION_TOKEN"]
            }
            if os.environ.get('AWS_REGION'):
                awsRegion = os.environ['AWS_REGION']
        else:
            print("Cannot use these credentials to open the AWS Console.", file=sys.stderr)
            exit(0)
        #format the credentials into a json formatted string
        jsonTempCredentials = json.dumps(temporaryCredentials)
        return jsonTempCredentials, awsRegion

    def get_temp_credentials_from_session(self, session):
        """
        Return the credentials required to make the aws request to
        get the signin token
        """
        if session.get('AccessKeyId') and session.get('SecretAccessKey') and session.get('SessionToken'):
            awsRegion = 'us-east-1'
            temporaryCredentials = {
                "sessionId": session['AccessKeyId'],
                "sessionKey": session['SecretAccessKey'],
            }
            if 'SessionToken' in session:
                temporaryCredentials["sessionToken"] = session["SessionToken"]
            if session.get('region'):
                awsRegion = session['region']

            #format the credentials into a json formatted string
            jsonTempCredentials = json.dumps(temporaryCredentials)
            return jsonTempCredentials, awsRegion
        print("Cannot use these credentials to open the AWS Console.", file=sys.stderr)
        exit(0)

    def make_aws_federation_request(self, temporaryCredentials):
        """
        temporaryCredentials - the credentials used to make the request;
        Make a request to the AWS federation endpoint to get a sign-in
        token, passing parameters in the query string.
        """
        params = {
            "Action": "getSigninToken",
            "Session": temporaryCredentials,
        }
        requestURL = "https://signin.aws.amazon.com/federation"
        response = requests.get(requestURL, params=params)
        return response

    def get_signin_token(self, awsResponse):
        """
        awsResponse - the response from AWS that contains the singin token;
        return the signin token from `awsResponse`
        """
        # The return value from the federation endpoint, the token.
        return json.loads(awsResponse.text)["SigninToken"]
        # Token is good for 15 minutes.

    def get_console_url(self, awsSigninToken, awsRegion):
        """
        awsSigninToken - the token used to sign into the AWS console;
        awsRegion - the region to sign into the console under;
        return the url that would sign the awsume'd user into the AWS console
        """
        # Create the URL to the console with token
        params = {
            "Action": "login",
            "Issuer": "",
            "Destination": "https://console.aws.amazon.com/console/home?region=" + awsRegion, ### SET THE REGION HERE TO THE CREDENTIALS REGION IF POSSIBLE
            "SigninToken": awsSigninToken
        }
        url = "https://signin.aws.amazon.com/federation?"
        url += urlencode(params)
        return url

    def open_browser_to_url(self, url):
        """
        url - the website to open;
        open the `url` in the appropriate browser
        """
        try:
            webbrowser.open(url)
        except Exception:
            print("Cannot open browser, here is the link:", file=sys.stderr)
            print(url, file=sys.stderr)
