@ECHO OFF

IF "%1"=="" GOTO displayUsage

IF "%2"=="refresh" (
  DEL "%userprofile%\.aws\cli\cache\%1*.json"
)

call aws s3 ls --profile %1 > nul

IF ERRORLEVEL 1 GOTO end

FOR /F %%M in ('DIR %userprofile%\.aws\cli\cache\%1*.json /B /S') DO (
  FOR /F tokens^=16^,20^,28^ delims^=^" %%G IN (%%M) DO (
    IF "%2"=="show" (
      ECHO.
      ECHO SET AWS_SECRET_ACCESS_KEY=%%G
      ECHO SET AWS_SESSION_TOKEN=%%H
      ECHO SET AWS_ACCESS_KEY_ID=%%I
    )
    SET AWS_SECRET_ACCESS_KEY=%%G
    SET AWS_SESSION_TOKEN=%%H
    SET AWS_ACCESS_KEY_ID=%%I
    GOTO setregion
  ) 
)

:setregion
call aws configure get region --profile %1 > awsume_region.txt
IF ERRORLEVEL 1 GOTO regionerror

SET /p AWS_REGION= < awsume_region.txt
SET /p AWS_DEFAULT_REGION= < awsume_region.txt
DEL "./awsume_region.txt"

IF "%2"=="show" (
  ECHO SET AWS_REGION=%AWS_REGION%
  ECHO SET AWS_DEFAULT_REGION=%AWS_DEFAULT_REGION%
)
GOTO :end

:regionerror
IF "%2"=="show" (
  ECHO "# No region set"
)
DEL "./awsume_region.txt"
GOTO :end


:displayUsage
ECHO.
ECHO Missing profile name
ECHO. 
ECHO Usage: awsume profile-name [show]
ECHO.
:end
