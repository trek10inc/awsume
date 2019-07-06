# Overview

## What is awsume?

Awsume is a command-line utility for retreiving and exporting AWS credentials to your shell's environment.

With awsume, you can get credentials for any profile located in your [config and credentials files](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html), including those that require MFA or an `assume-role` call.

## How does it work?

Awsume works by setting a number of environment variables in your shell. These are the credentials awsume will manage:

- `AWSUME_PROFILE`
- `AWS_PROFILE`
- `AWS_DEFAULT_PROFILE`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SECURITY_TOKEN`
- `AWS_SESSION_TOKEN`
- `AWS_REGION`
- `AWS_DEFAULT_REGION`

## Awsume vs Awsumepy

Because awsume requires the ability to manage your current shell's environment variables, it must be sourced (unless you're running on Windows). On unix-like systems, a subshell cannot update a parent shell's environment variables. Unfortunately, you cannot `source` a python script, so awsume is architected with a shell wrapper (awsume) around a python script (awsumepy).
