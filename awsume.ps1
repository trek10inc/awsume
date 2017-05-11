param (
    [string]$profileName = "default",
    [switch]$d = $false,
    [switch]$refresh = $false
)

function Remove-AwsEnvs() {
    $env:AWS_SECRET_ACCESS_KEY = ""
    $env:AWS_SESSION_TOKEN = ""
    $env:AWS_ACCESS_KEY_ID = ""
    $env:AWS_REGION = ""
    $env:AWS_DEFAULT_REGION = ""
}

function Get-SavedSession([string]$profileName) {
    $session = $null
    $tempProfile = "awsume-temp-$profileName"
    if (Test-Path "~\.aws\cli\cache\$tempProfile.json") {
        $session = Get-Content "~\.aws\cli\cache\$tempProfile.json" | ConvertFrom-Json
        $timeLeft = New-TimeSpan -Start (Get-Date) -End (Get-Date $session.Credentials.Expiration)
        if (0 -le $timeLeft.TotalMinutes -and $timeLeft.TotalMinutes -lt 10) {
            $x = [math]::Round($timeLeft.TotalMinutes)
            $refreshToken = Read-Host "About $x minutes remain, refresh token? [Y/n]"
            if ([string]::IsNullOrWhiteSpace($refreshToken) -or $refreshToken -like "Y") {
                $session = $null
            }
        }
    }
    return $session
}

function Get-ProfileName([string]$profileName) {
    if ($d -eq $false -and $profileName -eq "default") {
        $profileName = Read-Host -Prompt 'Enter the profile [default]'
        if ([string]::IsNullOrWhiteSpace($profileName) -or $profileName -eq "default") {
            $profileName = "default"
            Write-Host "In the future, you can use the -d flag to skip entering default"
        }
    }
    return $profileName
}

function Get-SourceProfile([string]$profileName) {
    $sourceProfile = aws configure get source_profile --profile $profileName
    if ([string]::IsNullOrWhiteSpace($sourceProfile)) {
        $sourceProfile = $profileName
    }
    return $sourceProfile
}

function Get-RoleArn([string]$profileName) {
    $roleArn = aws configure get role_arn --profile $profileName
    return $roleArn
}

function Get-MfaArn([string]$profileName) {
    $mfaArn = aws configure get mfa_serial --profile $profileName
    if ($LASTEXITCODE -gt 1) {
        exit # It can exist or not (0 or 1). That's ok but if it crashes, then we need to exit
    }
    return $mfaArn
}

function Set-Session([string]$profileName, [string]$mfaArn, [switch]$refresh) {
    $session = $null
    if (-Not $refresh) {
        $session = Get-SavedSession $profileName
    }
    if (-Not $session) {
        $secureMfaToken = Read-Host -AsSecureString "Enter MFA code"
        $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureMfaToken)
        $mfaToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)

        $session = aws sts get-session-token --serial-number $mfaArn --token-code $mfaToken --profile $profileName --output json | ConvertFrom-Json
    }
    Set-Environment $profileName $session
}

function Set-Environment([string]$profileName, $session) {
    $env:AWS_SECRET_ACCESS_KEY = $session.Credentials.SecretAccessKey
    $env:AWS_SESSION_TOKEN = $session.Credentials.SessionToken
    $env:AWS_ACCESS_KEY_ID = $session.Credentials.AccessKeyId
    $env:AWS_REGION = aws configure get region --profile $profileName
    $env:AWS_DEFAULT_REGION = aws configure get region --profile $profileName
    
    if (-Not (Test-Path "~\.aws\cli\cache\")) {
        mkdir "~\.aws\cli\cache\"
    }
    $tempProfile = "awsume-temp-$profileName"
    ConvertTo-Json $session | Out-File -Force -FilePath "~\.aws\cli\cache\$tempProfile.json"
}

function Set-AssumeRole([string]$profileName, [string]$sourceProfile, [string]$mfaArn, [string]$roleArn, [switch]$refresh) {
    Set-Session $sourceProfile $mfaArn $refresh
    $session = aws sts assume-role --role-arn $roleArn --role-session-name "awsume-temp-$profileName-$(Get-Random)" --output json | ConvertFrom-Json
    Set-Environment $profileName $session
}

Remove-AwsEnvs
$profileName = Get-ProfileName $profileName
$sourceProfile = Get-SourceProfile $profileName # Will be used for assuming roles
$roleArn = Get-RoleArn $profileName # Will be used for assuming roles
$mfaArn = Get-MfaArn $profileName
$assumeRole = -Not [string]::IsNullOrWhiteSpace($sourceProfile) -and -Not [string]::IsNullOrWhiteSpace($roleArn)

if ($assumeRole) {
    Set-AssumeRole $profileName $sourceProfile $mfaArn $roleArn $refresh
}
else {
    Set-Session $profileName $mfaArn $refresh
}
