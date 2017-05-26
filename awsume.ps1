Param (
    [string]$profileName = "default",
    [switch]$d = $false,
    [switch]$r = $false,
    [switch]$s = $false
)

function Get-SavedSession([string]$profileName) {
    $session = $null
    $tempProfile = "awsume-temp-$profileName"
    if (Test-Path "~\.aws\cli\cache\$tempProfile.json") {
        $session = Get-Content "~\.aws\cli\cache\$tempProfile.json" | ConvertFrom-Json
        Set-Environment $profileName $session

        aws sts get-caller-identity > $null
        if ( -not $? ) {
            #cache is invalid
            rm "~\.aws\cli\cache\$tempProfile.json"
            $session = $null
        }
    }
    return $session
}

function Set-Session([string]$profileName, [bool]$r) {
    $session = $null
    if (-Not $r) {
        $session = Get-SavedSession $profileName
    }
    if (-Not $session) {
        $mfaToken = Read-Host -Prompt "Enter MFA code"
        [string]$AWSUME_UserArn= aws sts get-caller-identity --region us-east-1 --query Arn --output text --profile $profileName
        [string]$AWSUME_MfaArn=$AWSUME_UserArn -replace "user", "mfa"
        $session = aws sts get-session-token --serial-number $AWSUME_MfaArn --token-code $mfaToken --profile $profileName --output json | ConvertFrom-Json

        #write the credentials to cache
        if (-Not (Test-Path "~\.aws\cli\cache\")) {
            mkdir "~\.aws\cli\cache\"
        }
        $tempProfile = "awsume-temp-$profileName"
        ConvertTo-Json $session | Out-File -Force -FilePath "~\.aws\cli\cache\$tempProfile.json"
    }
    Set-Environment $profileName $session
    Write-Host "#Source Profile Credentials ($profileName) expire:" $session.Credentials.Expiration
}

function Set-Environment([string]$profileName, $session) {
    $env:AWS_SECRET_ACCESS_KEY = $session.Credentials.SecretAccessKey
    $env:AWS_SESSION_TOKEN = $session.Credentials.SessionToken
    $env:AWS_SECURITY_TOKEN = $session.Credentials.SessionToken
    $env:AWS_ACCESS_KEY_ID = $session.Credentials.AccessKeyId
    $env:AWS_REGION = aws configure get region --profile $profileName
    $env:AWS_DEFAULT_REGION = $env:AWS_REGION
}

function Set-AssumeRole([string]$profileName, [string]$sourceProfile, [string]$roleArn, [bool]$r) {
    Set-Session $sourceProfile $r
    $session = aws sts assume-role --role-arn $roleArn --role-session-name "$profileName-$(Get-Random)" --output json | ConvertFrom-Json
    Set-Environment $profileName $session
    Write-Host "#Role Credentials ($profileName) expire:" $session.Credentials.Expiration
}

#Remove the environment variables associated with the AWS CLI,
#ensuring all environment variables will be valid
$env:AWS_SECRET_ACCESS_KEY = ""
$env:AWS_SESSION_TOKEN = ""
$env:AWS_SECURITY_TOKEN = ""
$env:AWS_ACCESS_KEY_ID = ""
$env:AWS_REGION = ""
$env:AWS_DEFAULT_REGION = ""

#validate the profileName, if parameter is empty, set it to default
if ($d -eq $false -or [string]::IsNullOrWhiteSpace($profileName)) {
        $profileName = "default"
}

#get the source profile, if there is none, set it to profile name
$sourceProfile = aws configure get source_profile --profile $profileName
if ([string]::IsNullOrWhiteSpace($sourceProfile)) {
    [bool]$AWSUME_IS_USER=$true
    $sourceProfile = $profileName
}

if ($AWSUME_IS_USER) {
    Set-Session $profileName $r
}
else {
    $roleArn = aws configure get role_arn --profile $profileName
    Set-AssumeRole $profileName $sourceProfile $roleArn $r
}

#IF SHOW THEN SHOW COMMANDS
if ($s){
    Write-Host "`$env:AWS_SECRET_ACCESS_KEY =" $env:AWS_SECRET_ACCESS_KEY
    Write-Host "`$env:AWS_SESSION_TOKEN =" $env:AWS_SESSION_TOKEN
    Write-Host "`$env:AWS_SECURITY_TOKEN =" $env:AWS_SECURITY_TOKEN
    Write-Host "`$env:AWS_ACCESS_KEY_ID =" $env:AWS_ACCESS_KEY_ID
    Write-Host "`$env:AWS_REGION =" $env:AWS_REGION
    Write-Host "`$env:AWS_DEFAULT_REGION =" $env:AWS_DEFAULT_REGION
}
