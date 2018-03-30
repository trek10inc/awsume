# AWSume Console Plugin

This is a plugin that enables you to use your assumed role credentials to open the AWS console in your default browser. To install, just place the `awsumeConsole.py` and `awsumeConsole.yapsy-plugin` within your `~/.aws/awsumePlugins` directory, as you would install any other AWSume plugin.

## Dependencies

This plugin does require you to have the python module `requests` installed, which can be done with a simple command:

```bash
pip install requests[security]
```

Note: the [security] specifier is not required if you have the latest version of pyopenssl installed on your system already.

## Installation

To install this plugin, using AWSume's latest `--install-plugin` feature, run:

``` bash
awsume --install-plugin https://raw.githubusercontent.com/trek10inc/awsume/master/examplePlugin/awsumeConsole.py https://raw.githubusercontent.com/trek10inc/awsume/master/examplePlugin/awsumeConsole.yapsy-plugin
```

## Use

There are two ways to use this plugin.

- Use your current environment variables to open the console
  - `awsume -c` Will open the AWS console using the current environment variables
- Use a profile_name
  - `awsume <profile_name> -c` Will run AWSume on `<profile_name>` as it normally would, but will open the console using the credentials from running AWSume on `<profile_name>`.

### Get Console Link

- If you want to get the url itself instead of trying to open the console, use:

``` bash
awsume <profile_name> -cl
```

or

``` bash
awsume <profile_name> --console-link
```
