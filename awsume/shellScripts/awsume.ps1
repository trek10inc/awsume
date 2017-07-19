<#
.Synopsis
    Assumes an AWS IAM role
.DESCRIPTION
    This script will reset all AWS environment variables,
    get the required credentials from the profile name,
    get a session security token for the source profile,
    if required, assume the role from the source profile,
    and set all of the AWS environment variables
.EXAMPLE
    awsume -d -r
    This will assume the role of the default profile,
    and force refresh the session token, requiring you
    to re-enter your MFA token
.EXAMPLE
    awsume profile_name -s
    This will assume the role of the profile named
    "profile_name", and will show the commands
    required to assume the same role.
.EXAMPLE
    awsume
    This will assume the default role
.LINK
    https://www.trek10.com/blog/awsume-aws-assume-made-awesome/
    https://github.com/trek10inc/awsume
#>

Param (
    [string]$AWSUME_PROFILE_NAME = "",
    [switch]$h = $false,
    [switch]$d = $false,
    [switch]$r = $false,
    [switch]$s = $false,
    [switch]$a = $false,
    [switch]$k = $false,
    [switch]$v = $false,
    [switch]$l = $false
)

if ($args) {
    Write-Warning "Unknown arguments: $args"
    exit 1
}

#check all of the parameter switches
$h_string = ""
if ($h) { $h_string = "-h"}
$d_string = ""
if ($d) { $d_string = "-d"}
$r_string = ""
if ($r) { $r_string = "-r"}
$s_string = ""
if ($s) { $s_string = "-s"}
$a_string = ""
if ($a) { $a_string = "-a"}
$k_string = ""
if ($k) { $k_string = "-k"}
$v_string = ""
if ($v) { $v_string = "-v"}
$l_string = ""
if ($l) { $l_string = "-l"}

#grab the environment variables from the python script
#AWSUME_FLAG - what awsumepy told the shell to do
#AWSUME_1 - secret access key / autoAwsumeProfileName
#AWSUME_2 - security token / fileName
#AWSUME_3 - access key id
#awsume_4 - region

$AWSUME_FLAG, $AWSUME_1, $AWSUME_2, $AWSUME_3, $AWSUME_4 = `
$(awsumepy $AWSUME_PROFILE_NAME $h_string $d_string $r_string $s_string $a_string $k_string $v_string $l_string) -split '\s+'

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

    if ($s) {
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
