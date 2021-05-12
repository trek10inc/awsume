@echo off

set SHOW=

awsumepy %* > %TEMP%\temp.txt
set AWSUME_STATUS=%ERRORLEVEL%
set /p AWSUME_TEXT=<%TEMP%\temp.txt
del %TEMP%\temp.txt

FOR %%A IN (%*) DO (
    IF "%%A"=="-s" (set "SHOW=y")
)

for /f "tokens=1,2,3,4,5,6,7,8 delims= " %%a in ("%AWSUME_TEXT%") do (
    if "%%a" == "usage:" (
        awsumepy %*
    )
    if "%%a" == "Version" (
        awsumepy %*
    )
    if "%%a" == "Listing..." (
        awsumepy %*
    )
    if "%%a" == "Auto" (
        set AWS_ACCESS_KEY_ID=
        set AWS_SECRET_ACCESS_KEY=
        set AWS_SESSION_TOKEN=
        set AWS_REGION=
        set AWS_DEFAULT_REGION=
        set AWS_PROFILE=
        set AWS_DEFAULT_PROFILE=
        set AWSUME_EXPIRATION=
        set AWSUME_PROFILE=
        set AWSUME_COMMAND=

        set AWSUME_COMMAND=%*
        set AWS_PROFILE=%%b
        set AWS_DEFAULT_PROFILE=%%b

        if "%%c" NEQ "None" (
            set AWS_REGION=%%c
            set AWS_DEFAULT_REGION=%%c)

        if "%%d" NEQ "None" (
            set AWSUME_PROFILE=%%d)

        start /min "autoawsume" autoawsume
    )
    if "%%a" == "Unset" (
        set AWS_ACCESS_KEY_ID=
        set AWS_SECRET_ACCESS_KEY=
        set AWS_SESSION_TOKEN=
        set AWS_REGION=
        set AWS_DEFAULT_REGION=
        set AWS_PROFILE=
        set AWS_DEFAULT_PROFILE=
        set AWSUME_EXPIRATION=
        set AWSUME_PROFILE=
        set AWSUME_COMMAND=

        IF defined SHOW (
            echo set AWS_ACCESS_KEY_ID=
            echo set AWS_SECRET_ACCESS_KEY=
            echo set AWS_SESSION_TOKEN=
            echo set AWS_REGION=
            echo set AWS_DEFAULT_REGION=
            echo set AWS_PROFILE=
            echo set AWS_DEFAULT_PROFILE=
            echo set AWSUME_EXPIRATION=
            echo set AWSUME_PROFILE=
            echo set AWSUME_COMMAND=
        )
    )
    if "%%a" == "Kill" (
        set AWS_ACCESS_KEY_ID=
        set AWS_SECRET_ACCESS_KEY=
        set AWS_SESSION_TOKEN=
        set AWS_REGION=
        set AWS_DEFAULT_REGION=
        set AWS_PROFILE=
        set AWS_DEFAULT_PROFILE=
        set AWSUME_EXPIRATION=
        set AWSUME_PROFILE=
        set AWSUME_COMMAND=
        taskkill /FI "WindowTitle eq autoawsume" > null 2>&1
    )
    if "%%a" == "Stop" (
        if "auto-refresh-%%b" == "%AWS_PROFILE%" (
            set AWS_ACCESS_KEY_ID=
            set AWS_SECRET_ACCESS_KEY=
            set AWS_SESSION_TOKEN=
            set AWS_REGION=
            set AWS_DEFAULT_REGION=
            set AWS_PROFILE=
            set AWS_DEFAULT_PROFILE=
            set AWSUME_EXPIRATION=
            set AWSUME_PROFILE=
            set AWSUME_COMMAND=
        )
    )
    if "%%a" == "Awsume" (
        set AWS_ACCESS_KEY_ID=
        set AWS_SECRET_ACCESS_KEY=
        set AWS_SESSION_TOKEN=
        set AWS_REGION=
        set AWS_DEFAULT_REGION=
        set AWS_PROFILE=
        set AWS_DEFAULT_PROFILE=
        set AWSUME_EXPIRATION=
        set AWSUME_PROFILE=
        set AWSUME_COMMAND=

        set AWSUME_COMMAND=%*
        if "%%b" NEQ "None" (
            set AWS_ACCESS_KEY_ID=%%b)

        if "%%c" NEQ "None" (
            set AWS_SECRET_ACCESS_KEY=%%c)

        if "%%d" NEQ "None" (
            set AWS_SESSION_TOKEN=%%d)

        if "%%e" NEQ "None" (
            set AWS_REGION=%%e
            set AWS_DEFAULT_REGION=%%e)

        if "%%f" NEQ "None" (
            set AWSUME_PROFILE=%%f)

        if "%%g" NEQ "None" (
            set AWS_PROFILE=%%g
            set AWS_DEFAULT_PROFILE=%%g)

        if "%%h" NEQ "None" (
            set AWSUME_EXPIRATION=%%h)

        IF defined SHOW (
            for /f "tokens=1,2,3,4,5 delims= " %%a in ("%AWSUME_TEXT%") do (
                if "%%b" NEQ "None" (
                    echo set AWS_ACCESS_KEY_ID=%%b)
                if "%%c" NEQ "None" (
                    echo set AWS_SECRET_ACCESS_KEY=%%c)

                if "%%d" NEQ "None" (
                    echo set AWS_SESSION_TOKEN=%%d)

                if "%%e" NEQ "None" (
                    echo set AWS_REGION=%%e
                    echo set AWS_DEFAULT_REGION=%%e)

                if "%%f" NEQ "None" (
                    echo set AWSUME_PROFILE=%%f)

                if "%%g" NEQ "None" (
                    echo set AWS_PROFILE=%%g
                    echo set AWS_DEFAULT_PROFILE=%%g)

                if "%%h" NEQ "None" (
                    echo set AWSUME_EXPIRATION=%%h)
            )
        )
    )
)

Exit /b %AWSUME_STATUS%
