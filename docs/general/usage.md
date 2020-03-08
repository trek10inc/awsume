# Usage

There's quite a few things awsume can do for you.

If you run `awsume -h` you can see a sizeable list of options (as of 4.0.0):

```bash
usage: awsume [-h] [-v] [-r] [-s] [-u] [-a] [-k] [-o] [-l [more]]
              [--refresh-autocomplete] [--role-arn role_arn]
              [--source-profile source_profile] [--external-id external_id]
              [--mfa-token mfa_token] [--region region]
              [--session-name session_name] [--role-duration role_duration]
              [--with-saml | --with-web-identity]
              [--credentials-file credentials_file] [--config-file config_file]
              [--config [option [option ...]]] [--info] [--debug]
              [profile_name]

Awsume - A cli that makes using AWS IAM credentials easy

positional arguments:
  profile_name                         The target profile name

optional arguments:
  -h, --help                           show this help message and exit
  -v, --version                        Display the current version of awsume
  -r, --refresh                        Force refresh credentials
  -s, --show-commands                  Show the commands to set the credentials
  -u, --unset                          Unset your aws environment variables
  -o, --output-profile output_profile  A profile to output credentials to
  -a, --auto-refresh                   Auto refresh credentials
  -k, --kill-refresher                 Kill autoawsume
  -l [more], --list-profiles [more]    List profiles, "more" for detail (slow)
  --role-arn role_arn                  Role ARN to assume
  --source-profile source_profile      source_profile to use (role-arn only)
  --external-id external_id            External ID to pass to the assume_role
  --mfa-token mfa_token                Your mfa token
  --region region                      The region you want to awsume into
  --session-name session_name          Set a custom role session name
  --role-duration role_duration        Seconds to get role creds for
  --with-saml                          Use saml (requires plugin)
  --with-web-identity                  Use web identity (requires plugin)
  --credentials-file credentials_file  Target a shared credentials file
  --config-file config_file            Target a config file
  --config [option [option ...]]       Configure awsume
  --list-plugins                       List installed plugins
  --info                               Print any info logs to stderr
  --debug                              Print any debug logs to stderr

Thank you for using AWSume! Check us out at https://trek10.com
```

## Refresh

The `--refresh` flag will tell awsume to ignore any cached credentials and get a new session token.

## Show Commands

The `--show-commands` flag will display the exact commands required to export awsume's credentials to a different shell session, like this:

```
$ awsume my-admin -s
export AWS_ACCESS_KEY_ID=<SECRET>
export AWS_SECRET_ACCESS_KEY=<SECRET
export AWS_SESSION_TOKEN=<SECRET>
export AWS_SECURITY_TOKEN=<SECRET>
export AWS_REGION=<REGION>
export AWS_DEFAULT_REGION=<REGION>
export AWSUME_PROFILE=my-admin
```

This way you can easily get credentials to another shell session, for instance through ssh.

This works on Bash, Zsh, Fish, PowerShell, and Windows Command Prompt.

## Unset

The `--unset` flag will clear your current shell's AWS environment variables.

## Output Profile

The `-o`/`--output-profile` flag will tell awsume to write awsume'd credentials to the specified output profile.

_Note: Awsume will not overwrite an existing profile that is not managed by awsume (noted by the `manager = awsume` property)._

## Auto Refresh

The `--auto-refresh` flag will tell awsume to automatically refresh the credentials. You can read more about how this works [here](../advanced/autoawsume.md).

## Kill Refresher

The `--kill-refresher` flag will handle stopping autoawsume from refreshing a profile. If you pass a profile name along with the flag, that profile will no longer be refreshed. If no profile name is passed along with this flag, then all auto-refreshed profiles will be stopped.

## List Profiles

The `--list-profiles` flag will list data on all of the profiles it has available to it (from the config and shared credentials files or any plugins).

If you supply an additional argument "more" to this flag, you can tell awsume to get more data than what is present locally. Currently this only means making the `sts.get_caller_identity` call to get the account ID if it can't derive it from a `role_arn` or `mfa_serial`, which will of course be slower.

```
========================AWS Profiles=======================
PROFILE         TYPE  SOURCE  MFA?  REGION     ACCOUNT
app-dev         User  None    No    us-east-1  Unavailable
app-staging     User  None    No    us-east-1  Unavailable
app-prod        User  None    No    us-east-1  Unavailable
iam             User  None    No    us-east-1  Unavailable
client-dev      Role  iam     Yes   us-west-2  123123123123
client-staging  Role  iam     Yes   us-west-2  234234234234
client-prod     Role  iam     Yes   us-west-2  345345345345
```

In this case, if `TYPE` is a "role", it has a `role_arn`. If it does not have a `role_arn`, it will be classified as a "user" profile type.

## Refresh Autocomplete

In order to keep autocomplete fast, we do not make use of any of awsumepy's modules or any `pkg_resources` slow entry points. However, this means that any plugins that supply profiles won't be able to supply autocomplete with their profile names. To circumvent this, we utilize an autocomplete file located at `~/.awsume/autocomplete.json`. When you pass the `--refresh-autocomplete` flag to awsume, it makes the calls to all plugins to collect all profile names together into that file. That way, when the `awsume-autocomplete` helper is called, it simply reads from the config and credentials files, and the `~/.awsume/autocomplete.json` file to return a list of awsume-able profile names.

## Role ARN

As of awsume 4, you can use the `--role-arn` flag to awsume a specific role using your current credentials. You can also use a shorthand that follows the following format: `<account_id>:<role_name>`. This way you can role-chain as much as you want.

## Source Profile

To help with the Role ARN flag, you can pass in a `--source-profile` flag to target a specific profile to be the source of the `assume_role` call for the given role arn.

## External ID

If you don't have an external ID for your role present in your config or credentials files, you can supply this through the command line with the `--external-id` flag.

## MFA Token

If you want to supply the mfa token through the CLI without the interactive prompt, you can supply the `--mfa-token` flag with your mfa code.

## Region

You can target a specific region to awsume with the `--region` flag. This basically amounts to setting the `AWS_REGION` and `AWS_DEFAULT_REGION` environment variables. Useful for overriding the region found in a config profile.

## Session Name

You can supply your own session name to the `assume_role` call with the `--session-name` flag.

## Role Duration

You can also supply a custom role duration (up to 43200) for the number of seconds to request role credentials for with the `--role-duration` flag.

## With SAML

The `--with-saml` flag will tell awsume to invoke any `assume_role_with_saml` plugins you have installed. There is no default implementation for this.

## With Web Identity

The `--with-web-identity` flag will tell awsume to invoke any `assume_role_with_web_identity` plugins you have installed. There is no default implementation for this.

## Credentials File

With the `--credentials-file` flag, you can target a credentials file to use, instead of the default `~/.aws/credentials` file or whatever is pointed to with the `AWS_SHARED_CREDENTIALS_FILE` environment variable.

## Config File

With the `--config-file` flag, you can target a config file to use, instead of the default `~/.aws/config` file or whatever is pointed to with the `AWS_CONFIG_FILE` environment variable.

## Config

The `--config` flag will help you configure awsume and any plugins making use of the configuration system. See the [config documentation](./config) for more details.

## List Plugins

This will list all of the currently-installed awsume plugins.

## Info

The `--info` flag will display any INFO-level logs.

## Debug

The `--debug` flag will display any DEBUG-level logs.
