# Overview

## What is awsume?

Awsume is a command-line utility for retrieving and exporting AWS credentials to your shell's environment.

With awsume, you can get credentials for any profile located in your [config and credentials files](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html), including those that require MFA or an `assume-role` call.

## How does it work?

Awsume works by setting a number of environment variables in your shell. These are the credentials awsume will manage:

- `AWSUME_PROFILE`
- `AWSUME_COMMAND`
- `AWS_PROFILE`
- `AWS_DEFAULT_PROFILE`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SECURITY_TOKEN`
- `AWS_SESSION_TOKEN`
- `AWS_REGION`
- `AWS_DEFAULT_REGION`

## Features

- Reads your credentials from `~/.aws/config` and `~/.aws/credentials`
- Extensible - add custom hooks to make awsume do whatever you need it to (SAML provider, profile provider, etc.)
- Set your environment variables to your AWS credentials so any cli/api call you make uses those credentials
- Use MFA-authenticated credentials on the command-line
- Use assume-role credentials to your on the command-line
- Cache MFA-authenticated credentials for up to 12 hours
- Role-chain as many role assumptions as you need
- Show the commands you need to export environment variables in another terminal (`awsume -s`)
- Export awsume'd credentials into a profile in the `~/.aws/config` and `~/.aws/credentials` files (`awsume -o`)
- Auto-refresh assume-role credentials as long as source credentials are valid, up to 12 hours (`awsume -a`)
- Get a pretty listing of your awsume-able profiles (`awsume -l`)
- Autocomplete your awsume-able profiles
- Assume arbitrary role-arns from the command-line, using full role arn or short-hand syntax (with optional partition defaulting to `aws`, `awsume --role-arn [partition]:{account_id}:{role_name}`)
- Set a custom session name for assume-role credentials (`awsume --session-name`)
- Assume a role for a custom duration for up to 12 hours or whatever the role's maximum is configured as (`awsume --role-duration`)
- Use separate config/credentials files, also supports the appropriate environment variables (`awsume --config-file ... --credentials-file ...`)

## Terminology

- **role profile** is a profile that contains a `role_arn` property, and either a `source_profile` or `credential_source` property.
- **non-role profile** / **user profile** is a profile that does not have a `role_arn` property. It is typically a profile that has access keys for a user. However it can also refer to profiles that have temporary session token credentials in them, which may or may not be role credentials.

## Awsume vs Awsumepy

Because awsume requires the ability to manage your current shell's environment variables, it must be sourced (unless you're running on Windows). On unix-like systems, a subshell cannot update a parent shell's environment variables. Unfortunately, you cannot `source` a python script, so awsume is architected with a shell wrapper (awsume) around a python script (awsumepy).

When given a role profile that uses a source_profile which requires MFA, awsume will make the `get-session-token` call with the source_profile to get 12-hour long credentials. It will then cache those MFA-authenticated credentials. Then it will make the `assume-role` call to get credentials for the requested amount of time (AWS has a default of 1 hour maximum role credentials). When those role credentials run out, you can re-execute awsume, and awsume will use those cache'd MFA-authenticated credentials to get new role credentials for you, without re-prompting you for your MFA token. This can be automated with [autoawsume](/advanced/autoawsume), but this is the typical use-case for awsume.

If you give awsume a non-role profile that doesn't require MFA (no `mfa_serial`), it will simply export those credentials found in the profile.

If you give awsume a non-role profile that does require MFA, it will check the cache for the profile's credentials, and if the cache'd credentials either don't exist or are expired, it will make the get-session-token call to get new ones and cache those to. However if the cache exists and is valid, it'll use those credentials without prompting for MFA.

When assuming a role, awsume will set the session name to the profile name you gave awsume, however this can be changed with `--session-name` (see the [usage](/general/usage) for more details).

Awsume uses the `~/.awsume/cache/` directory to store cache'd credentials. It stores credentials by access key ID, so the case multiple profiles have the same access keys, it'll be cached the same.
