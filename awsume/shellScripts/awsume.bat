@echo off

set SHOW=

awsumepy %* > ./temp.txt
set /p AWSUME_TEXT=<./temp.txt

for /f "tokens=1,2,3,4,5,6 delims= " %%a in ("%AWSUME_TEXT%") do (
    if "%%a" == "Auto" (
        set AWS_SECRET_ACCESS_KEY=
        set AWS_SESSION_TOKEN=
        set AWS_SECURITY_TOKEN=
        set AWS_ACCESS_KEY_ID=
        set AWS_REGION=
        set AWS_DEFAULT_REGION=
        set AWS_PROFILE=
        set AWS_DEFAULT_PROFILE=
        set AWSUME_PROFILE=

        set AWS_PROFILE=%%b
        set AWS_DEFAULT_PROFILE=%%b
        set AWSUME_PROFILE=%%c
        start /min "autoAwsume" autoAwsume
    )
    if "%%a" == "Version" (
        awsumepy -v
    )
    if "%%a" == "Listing..." (
        awsumepy -l
    )
    if "%%a" == "Kill" (
        set AWS_SECRET_ACCESS_KEY=
        set AWS_SESSION_TOKEN=
        set AWS_SECURITY_TOKEN=
        set AWS_ACCESS_KEY_ID=
        set AWS_REGION=
        set AWS_DEFAULT_REGION=
        set AWS_PROFILE=
        set AWS_DEFAULT_PROFILE=
        set AWSUME_PROFILE=
        taskkill /FI "WindowTitle eq autoAwsume" > null 2>&1
    )
    if "%%a" == "Stop" (
        if "auto-refresh-%%b" == "%AWS_PROFILE%" (
        set AWS_PROFILE=
        set AWS_DEFAULT_PROFILE=
        )
    )
    if "%%a" == "Awsume" (
        set AWS_SECRET_ACCESS_KEY=
        set AWS_SESSION_TOKEN=
        set AWS_SECURITY_TOKEN=
        set AWS_ACCESS_KEY_ID=
        set AWS_REGION=
        set AWS_DEFAULT_REGION=
        set AWS_PROFILE=
        set AWS_DEFAULT_PROFILE=
        set AWSUME_PROFILE=

        set AWS_ACCESS_KEY_ID=%%b
        set AWS_SECRET_ACCESS_KEY=%%c

        if "%%d" NEQ "None" (
            set AWS_SESSION_TOKEN=%%d
            set AWS_SECURITY_TOKEN=%%d)


        if "%%e" NEQ "None" (
            set AWS_REGION=%%e
            set AWS_DEFAULT_REGION=%%e)

        set AWSUME_PROFILE=%%f
    )
)

IF defined SHOW (
    for /f "tokens=1,2,3,4,5 delims= " %%a in ("%AWSUME_TEXT%") do (
    if "%%a" == "Awsume" (
        echo set AWS_SECRET_ACCESS_KEY=%%b
        echo set AWS_ACCESS_KEY_ID=%%d

        if "%%c" NEQ "None" (
            echo set AWS_SESSION_TOKEN=%%c
            echo set AWS_SECURITY_TOKEN=%%c)

        if "%%e" NEQ "None" (
            echo set AWS_REGION=%%e
            echo set AWS_DEFAULT_REGION=%%e)

        echo set AWSUME_PROFILE=%%f
    ) else (echo "Invalid")
    )
)
