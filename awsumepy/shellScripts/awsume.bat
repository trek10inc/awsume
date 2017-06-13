@echo off
set AWSUMEPY_LOCATION="./awsume.py"

set AWS_SECRET_ACCESS_KEY=
set AWS_SESSION_TOKEN=
set AWS_SECURITY_TOKEN=
set AWS_ACCESS_KEY_ID=
set AWS_REGION=
set AWS_DEFAULT_REGION=
set SHOW=

python %AWSUMEPY_LOCATION% %* > ./temp.txt
set /p AWSUME_TEXT=<./temp.txt

FOR %%A IN (%*) DO (
    IF "%%A"=="-s" (set "SHOW=y")
)

for /f "tokens=1,2,3,4,5 delims= " %%a in ("%AWSUME_TEXT%") do (
    if "%%a" == "True" (
        set AWS_SECRET_ACCESS_KEY=%%b
        set AWS_SESSION_TOKEN=%%c
        set AWS_SECURITY_TOKEN=%%c
        set AWS_ACCESS_KEY_ID=%%d
        if "%%e" NEQ "None" (
            set AWS_REGION=%%e
            set AWS_DEFAULT_REGION=%%e)
    ) else (echo "Invalid")    
)

IF defined SHOW (
    for /f "tokens=1,2,3,4,5 delims= " %%a in ("%AWSUME_TEXT%") do (
    if "%%a" == "True" (
        echo set AWS_SECRET_ACCESS_KEY=%%b
        echo set AWS_SESSION_TOKEN=%%c
        echo set AWS_SECURITY_TOKEN=%%c
        echo set AWS_ACCESS_KEY_ID=%%d
        if "%%e" NEQ "None" (
            echo set AWS_REGION=%%e
            echo set AWS_DEFAULT_REGION=%%e)
    ) else (echo "Invalid")    
    )
)