#Author: Michael Barney, Trek10 Intern
#Date: June 2, 2017
#AWSume - a powershell script to assume an AWS IAM role from the command-line

#grab the environment variables from the python script
#AWSUME_FLAG - what awsumepy told the shell to do
#AWSUME_1 - secret access key / autoAwsumeProfileName
#AWSUME_2 - security token / fileName
#AWSUME_3 - access key id
#awsume_4 - region
$AWSUME_FLAG, $AWSUME_1, $AWSUME_2, $AWSUME_3, $AWSUME_4 = `
$(awsumepy $args) -split '\s+'

#if incorrect flag/help
if ( $AWSUME_FLAG -eq "usage:" ) {
    $(awsumepy -h)
}
#if version flag
elseif ( $AWSUME_FLAG -eq "Version" ) {
    Write-Host $AWSUME_1
}
#set up auto-refreshing role
elseif ( $AWSUME_FLAG -eq "Auto" ) {
    #Remove the environment variables associated with the AWS CLI,
    #ensuring all environment variables will be valid
    $env:AWS_SECRET_ACCESS_KEY = ""
    $env:AWS_SESSION_TOKEN = ""
    $env:AWS_SECURITY_TOKEN = ""
    $env:AWS_ACCESS_KEY_ID = ""
    $env:AWS_REGION = ""
    $env:AWS_DEFAULT_REGION = ""
    $env:AWS_PROFILE = ""
    $env:AWS_DEFAULT_PROFILE = ""
    #set the profile that will contain the session credentials
    $env:AWS_PROFILE = $AWSUME_1
    $env:AWS_DEFAULT_PROFILE = $AWSUME_1
    #run the background autoAwsume process
    Start-Process powershell -ArgumentList "autoAwsume" -WindowStyle hidden

}
#if user sent kill flag
elseif ( $AWSUME_FLAG -eq "Kill" ) {
    $env:AWS_PROFILE = ""
    $env:AWS_DEFAULT_PROFILE = ""
    exit
}
elseif ( $AWSUME_FLAG -eq "Stop" ) {
    if ( "auto-refresh-$AWSUME_1" -eq "$env:AWS_PROFILE" ) {
        $env:AWS_PROFILE = ""
        $env:AWS_DEFAULT_PROFILE = ""
    }
}
#awsume the profile
elseif ( $AWSUME_FLAG -eq "Awsume") {
    #Remove the environment variables associated with the AWS CLI,
    #ensuring all environment variables will be valid
    $env:AWS_SECRET_ACCESS_KEY = ""
    $env:AWS_SESSION_TOKEN = ""
    $env:AWS_SECURITY_TOKEN = ""
    $env:AWS_ACCESS_KEY_ID = ""
    $env:AWS_REGION = ""
    $env:AWS_DEFAULT_REGION = ""
    $env:AWS_PROFILE = ""
    $env:AWS_DEFAULT_PROFILE = ""

    $env:AWS_SECRET_ACCESS_KEY = $AWSUME_1
    $env:AWS_ACCESS_KEY_ID = $AWSUME_3
    
    if ( $AWSUME_2 -ne "None" ) {
        $env:AWS_SESSION_TOKEN = $AWSUME_2
        $env:AWS_SECURITY_TOKEN = $AWSUME_2
    }

    if ( $AWSUME_4 -ne "None" ) {
        $env:AWS_REGION = $AWSUME_4
        $env:AWS_DEFAULT_REGION = $AWSUME_4
    }

    #if enabled, show the exact commands to use in order to assume the role we just assumed
    if ($args -like "-s") {
        Write-Host "`$env:AWS_SECRET_ACCESS_KEY =" $env:AWS_SECRET_ACCESS_KEY
        Write-Host "`$env:AWS_ACCESS_KEY_ID =" $env:AWS_ACCESS_KEY_ID
        
        if ( $AWSUME_2 -ne "None" ) {
            Write-Host "`$env:AWS_SESSION_TOKEN =" $env:AWS_SESSION_TOKEN
            Write-Host "`$env:AWS_SECURITY_TOKEN =" $env:AWS_SECURITY_TOKEN
        }
            
        if ( $AWSUME_4 -ne "None" ) {
            Write-Host "`$env:AWS_REGION =" $env:AWS_REGION
            Write-Host "`$env:AWS_DEFAULT_REGION =" $env:AWS_DEFAULT_REGION
        }
    }
}
