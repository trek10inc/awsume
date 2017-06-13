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
    [string]$AWSUME_PROFILE_NAME = "default",
    [switch]$d = $false,
    [switch]$r = $false,
    [switch]$s = $false
)
if ($args) {
    Write-Warning "Unknown arguments: $args"
    exit 1
}


#Remove the environment variables associated with the AWS CLI,
#ensuring all environment variables will be valid
$env:AWS_SECRET_ACCESS_KEY = ""
$env:AWS_SESSION_TOKEN = ""
$env:AWS_SECURITY_TOKEN = ""
$env:AWS_ACCESS_KEY_ID = ""
$env:AWS_REGION = ""
$env:AWS_DEFAULT_REGION = ""

$d_string = ""
if ($d) { $d_string = "-d"}
$r_string = ""
if ($r) { $r_string = "-r"}
$s_string = ""
if ($s) { $s_string = "-s"}
Write-Host $d_string
$AWSUME_VALID,$AWSUME_SECRET_ACCESS_KEY,$AWSUME_SECURITY_TOKEN,$AWSUME_ACCESS_KEY_ID,$AWSUME_REGION = `
$(awsumepy $AWSUME_PROFILE_NAME $d_string $r_string $s_string) -split '\s+'

if ( $AWSUME_VALID = "True" ) {
    $env:AWS_SECRET_ACCESS_KEY = $AWSUME_SECRET_ACCESS_KEY
    $env:AWS_SESSION_TOKEN = $AWSUME_SECURITY_TOKEN
    $env:AWS_SECURITY_TOKEN = $AWSUME_SECURITY_TOKEN
    $env:AWS_ACCESS_KEY_ID = $AWSUME_ACCESS_KEY_ID

    if ( $AWSUME_REGION -ne "None" ) {
        $env:AWS_REGION = $AWSUME_REGION
        $env:AWS_DEFAULT_REGION = $AWSUME_REGION
    }
}

if ($s) {
    Write-Host "`$env:AWS_SECRET_ACCESS_KEY =" $env:AWS_SECRET_ACCESS_KEY
    Write-Host "`$env:AWS_SESSION_TOKEN =" $env:AWS_SESSION_TOKEN
    Write-Host "`$env:AWS_SECURITY_TOKEN =" $env:AWS_SECURITY_TOKEN
    Write-Host "`$env:AWS_ACCESS_KEY_ID =" $env:AWS_ACCESS_KEY_ID
    if ( $AWSUME_REGION -ne "None" ) {
        Write-Host "`$env:AWS_REGION =" $env:AWS_REGION
        Write-Host "`$env:AWS_DEFAULT_REGION =" $env:AWS_DEFAULT_REGION
    }
}