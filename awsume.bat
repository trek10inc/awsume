@ECHO OFF

IF "%1"=="" GOTO displayUsage

IF "%2"=="refresh" (
  del "%userprofile%\.aws\cli\cache\%1*.json"
)

aws s3 ls --profile %1 > nul

IF ERRORLEVEL 1 GOTO end

FOR /F %%M in ('DIR %userprofile%\.aws\cli\cache\%1*.json /B /S') DO (
  FOR /F tokens^=16^,20^,28^ delims^=^" %%G IN (%%M) DO (
    IF "%2"=="show" (
      echo.
      echo SET AWS_SECRET_ACCESS_KEY=%%G
      echo SET AWS_SESSION_TOKEN=%%H
      echo SET AWS_ACCESS_KEY_ID=%%I
    )
    SET AWS_SECRET_ACCESS_KEY=%%G
    SET AWS_SESSION_TOKEN=%%H
    SET AWS_ACCESS_KEY_ID=%%I
    GOTO end
  ) 
)


:displayUsage
echo.
echo Missing profile name
echo. 
echo Usage: assume profile-name [show]
echo.
:end
