#AWSume - a powershell script to assume an AWS IAM role from the command-line

#AWSUME_FLAG - what awsumepy told the shell to do
#AWSUME_n - the data from awsumepy
$AWSUME_FLAG, $AWSUME_1, $AWSUME_2, $AWSUME_3, $AWSUME_4, $AWSUME_5 = `
$(awsumepy $args) -split '\s+'

#if incorrect flag/help
if ( $AWSUME_FLAG -eq "usage:" ) {
    $(awsumepy -h)
}
#if version flag
elseif ( $AWSUME_FLAG -eq "Version" ) {
    $(awsumepy -v)
}
#if -l flag passed
elseif ( $AWSUME_FLAG -eq "Listing..." ) {
    $(awsumepy -l)
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
    $env:AWSUME_PROFILE = ""

    #set the profile that will contain the session credentials
    $env:AWS_PROFILE = $AWSUME_1
    $env:AWS_DEFAULT_PROFILE = $AWSUME_1
    $env:AWSUME_PROFILE = $AWSUME_2

    #run the background autoAwsume process
    Start-Process powershell -ArgumentList "autoAwsume" -WindowStyle hidden
}

#if user sent kill flag
elseif ( $AWSUME_FLAG -eq "Kill" ) {
    $env:AWS_SECRET_ACCESS_KEY = ""
    $env:AWS_SESSION_TOKEN = ""
    $env:AWS_SECURITY_TOKEN = ""
    $env:AWS_ACCESS_KEY_ID = ""
    $env:AWS_REGION = ""
    $env:AWS_DEFAULT_REGION = ""
    $env:AWS_PROFILE = ""
    $env:AWS_DEFAULT_PROFILE = ""
    $env:AWSUME_PROFILE = ""
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
    $env:AWSUME_PROFILE = ""

    $env:AWS_ACCESS_KEY_ID = $AWSUME_1
    $env:AWS_SECRET_ACCESS_KEY = $AWSUME_2

    if ( $AWSUME_3 -ne "None" ) {
        $env:AWS_SESSION_TOKEN = $AWSUME_3
        $env:AWS_SECURITY_TOKEN = $AWSUME_3
    }

    if ( $AWSUME_4 -ne "None" ) {
        $env:AWS_REGION = $AWSUME_4
        $env:AWS_DEFAULT_REGION = $AWSUME_4
    }

    $env:AWSUME_PROFILE = $AWSUME_5

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

        Write-Host "`$env:AWSUME_PROFILE =" $env:AWSUME_PROFILE
    }
}
