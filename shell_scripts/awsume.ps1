#AWSume - a powershell script to assume an AWS IAM role from the command-line

#AWSUME_FLAG - what awsumepy told the shell to do
#AWSUME_n - the data from awsumepy
$AWSUME_FLAG, $AWSUME_1, $AWSUME_2, $AWSUME_3, $AWSUME_4, $AWSUME_5, $AWSUME_6, $AWSUME_7 = `
$(awsumepy $args) -split '\s+'
$env:AWSUME_STATUS = $LASTEXITCODE

#if incorrect flag/help
if ( $AWSUME_FLAG -eq "usage:" ) {
    $(awsumepy $args)
}
#if version flag
elseif ( $AWSUME_FLAG -eq "Version" ) {
    $(awsumepy $args)
}
#if -l flag passed
elseif ( $AWSUME_FLAG -eq "Listing..." ) {
    $(awsumepy $args)
}
#set up auto-refreshing role
elseif ( $AWSUME_FLAG -eq "Auto" ) {
    #Remove the environment variables associated with the AWS CLI,
    #ensuring all environment variables will be valid
    $env:AWS_ACCESS_KEY_ID = ""
    $env:AWS_SECRET_ACCESS_KEY = ""
    $env:AWS_SESSION_TOKEN = ""
    $env:AWS_REGION = ""
    $env:AWS_DEFAULT_REGION = ""
    $env:AWS_PROFILE = ""
    $env:AWS_DEFAULT_PROFILE = ""
    $env:AWSUME_EXPIRATION = ""
    $env:AWSUME_PROFILE = ""
    $env:AWSUME_COMMAND = ""

    $env:AWSUME_COMMAND=$args
    #set the profile that will contain the session credentials
    $env:AWS_PROFILE = $AWSUME_1
    $env:AWS_DEFAULT_PROFILE = $AWSUME_1

    if ( $AWSUME_2 -ne "None" ) {
        $env:AWS_REGION = $AWSUME_2
        $env:AWS_DEFAULT_REGION = $AWSUME_2
    }

    if ( $AWSUME_3 -ne "None" ) {
        $env:AWSUME_PROFILE = $AWSUME_3
    }

    #run the background autoawsume process
    Start-Process powershell -ArgumentList "autoawsume" -WindowStyle hidden
}

#if user sent kill flag
elseif ( $AWSUME_FLAG -eq "Unset" ) {
    $env:AWS_ACCESS_KEY_ID = ""
    $env:AWS_SECRET_ACCESS_KEY = ""
    $env:AWS_SESSION_TOKEN = ""
    $env:AWS_REGION = ""
    $env:AWS_DEFAULT_REGION = ""
    $env:AWS_PROFILE = ""
    $env:AWS_DEFAULT_PROFILE = ""
    $env:AWSUME_EXPIRATION = ""
    $env:AWSUME_PROFILE = ""
    $env:AWSUME_COMMAND = ""

    #show the commands to unset these environment variables
    if ($args -like "-s") {
        Write-Host "`$env:AWS_ACCESS_KEY_ID = `"`""
        Write-Host "`$env:AWS_SECRET_ACCESS_KEY = `"`""
        Write-Host "`$env:AWS_SESSION_TOKEN = `"`""
        Write-Host "`$env:AWS_REGION = `"`""
        Write-Host "`$env:AWS_DEFAULT_REGION = `"`""
        Write-Host "`$env:AWS_PROFILE = `"`""
        Write-Host "`$env:AWS_DEFAULT_PROFILE = `"`""
        Write-Host "`$env:AWSUME_EXPIRATION = `"`""
        Write-Host "`$env:AWSUME_PROFILE = `"`""
        Write-Host "`$env:AWSUME_COMMAND = `"`""
    }
    exit
}
#if user sent kill flag
elseif ( $AWSUME_FLAG -eq "Kill" ) {
    $env:AWS_ACCESS_KEY_ID = ""
    $env:AWS_SECRET_ACCESS_KEY = ""
    $env:AWS_SESSION_TOKEN = ""
    $env:AWS_REGION = ""
    $env:AWS_DEFAULT_REGION = ""
    $env:AWS_PROFILE = ""
    $env:AWS_DEFAULT_PROFILE = ""
    $env:AWSUME_EXPIRATION = ""
    $env:AWSUME_PROFILE = ""
    $env:AWSUME_COMMAND = ""
    exit
}
elseif ( $AWSUME_FLAG -eq "Stop" ) {
    if ( "auto-refresh-$AWSUME_1" -eq "$env:AWS_PROFILE" ) {
        $env:AWS_ACCESS_KEY_ID = ""
        $env:AWS_SECRET_ACCESS_KEY = ""
        $env:AWS_SESSION_TOKEN = ""
        $env:AWS_REGION = ""
        $env:AWS_DEFAULT_REGION = ""
        $env:AWS_PROFILE = ""
        $env:AWS_DEFAULT_PROFILE = ""
        $env:AWSUME_EXPIRATION = ""
        $env:AWSUME_PROFILE = ""
        $env:AWSUME_COMMAND = ""
    }
}

#awsume the profile
elseif ( $AWSUME_FLAG -eq "Awsume") {
    #Remove the environment variables associated with the AWS CLI,
    #ensuring all environment variables will be valid
    $env:AWS_ACCESS_KEY_ID = ""
    $env:AWS_SECRET_ACCESS_KEY = ""
    $env:AWS_SESSION_TOKEN = ""
    $env:AWS_REGION = ""
    $env:AWS_DEFAULT_REGION = ""
    $env:AWS_PROFILE = ""
    $env:AWS_DEFAULT_PROFILE = ""
    $env:AWSUME_EXPIRATION = ""
    $env:AWSUME_PROFILE = ""
    $env:AWSUME_COMMAND = ""

    $env:AWSUME_COMMAND=$args
    if ( $AWSUME_1 -ne "None" ) {
        $env:AWS_ACCESS_KEY_ID = $AWSUME_1
    }
    if ( $AWSUME_2 -ne "None" ) {
        $env:AWS_SECRET_ACCESS_KEY = $AWSUME_2
    }

    if ( $AWSUME_3 -ne "None" ) {
        $env:AWS_SESSION_TOKEN = $AWSUME_3
    }

    if ( $AWSUME_4 -ne "None" ) {
        $env:AWS_REGION = $AWSUME_4
        $env:AWS_DEFAULT_REGION = $AWSUME_4
    }

    if ( $AWSUME_5 -ne "None" ) {
        $env:AWSUME_PROFILE = $AWSUME_5
    }

    if ( $AWSUME_6 -ne "None" ) {
        $env:AWS_PROFILE = $AWSUME_6
        $env:AWS_DEFAULT_PROFILE = $AWSUME_6
    }

    if ( $AWSUME_7 -ne "None" ) {
        $env:AWSUME_EXPIRATION = $AWSUME_7
    }

    #if enabled, show the exact commands to use in order to assume the role we just assumed
    if ($args -like "-s") {
        if ( $AWSUME_1 -ne "None" ) {
            Write-Host "`$env:AWS_ACCESS_KEY_ID =" $env:AWS_ACCESS_KEY_ID
        }
        if ( $AWSUME_2 -ne "None" ) {
            Write-Host "`$env:AWS_SECRET_ACCESS_KEY =" $env:AWS_SECRET_ACCESS_KEY
        }

        if ( $AWSUME_3 -ne "None" ) {
            Write-Host "`$env:AWS_SESSION_TOKEN =" $env:AWS_SESSION_TOKEN
        }

        if ( $AWSUME_4 -ne "None" ) {
            Write-Host "`$env:AWS_REGION =" $env:AWS_REGION
            Write-Host "`$env:AWS_DEFAULT_REGION =" $env:AWS_DEFAULT_REGION
        }

        if ( $AWSUME_5 -ne "None" ) {
            Write-Host "`$env:AWSUME_PROFILE =" $env:AWSUME_PROFILE
        }

        if ( $AWSUME_6 -ne "None" ) {
            Write-Host "`$env:AWS_PROFILE =" $AWSUME_6
            Write-Host "`$env:AWS_DEFAULT_PROFILE =" $AWSUME_6
        }

        if ( $AWSUME_7 -ne "None" ) {
            Write-Host "`$env:AWSUME_EXPIRATION = $AWSUME_7"
        }
    }
}

exit $env:AWSUME_STATUS
