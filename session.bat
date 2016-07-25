@ECHO OFF

:: CHECK PARAMETERS
IF "%1"=="" GOTO errorCheckParams :: TOKEN
IF "%2"=="" GOTO errorCheckParams :: PROFILE

:: CAPTURING STDERR 
aws --output text --profile %2 iam get-user 2> mfa_serial.txt 

:: EXTRACTING MFA SERIAL ARN
FOR /f "tokens=12" %%G IN (mfa_serial.txt) DO SET MFA_SERIAL=%%G 
SET MFA_SERIAL=%MFA_SERIAL:user=mfa%
DEL "./mfa_serial.txt"

:: GETTING SESSION DATA
aws --output text sts get-session-token --serial-number %MFA_SERIAL% --token-code %1 --profile %2 > session.txt

IF %ERRORLEVEL% NEQ 0 GOTO errorGetSession

:: SETTING VARIABLES
FOR /f "tokens=2" %%G IN (session.txt) DO SET AWS_ACCESS_KEY_ID=%%G
FOR /f "tokens=4" %%G IN (session.txt) DO SET AWS_SECRET_ACCESS_KEY=%%G
FOR /f "tokens=5" %%G IN (session.txt) DO SET AWS_SESSION_TOKEN=%%G
DEL "./session.txt"

ECHO Successfully set variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN

GOTO eof

:: ERROR HANDLING
:errorCheckParams
ECHO "Please pass an MFA token and a configured aws cli profile name, in that order"
GOTO eof

:errorGetUser
ECHO "Error getting user IAM details make sure second parameter is valid profile"
GOTO eof

:errorGetSession
DEL "./session.txt"
ECHO "Error getting user STS session details make sure MFA device is in-sync and entered token is correct"

:eof