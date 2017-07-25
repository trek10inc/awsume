# AWSume Plugins!

AWSume is now extensible, you can write your own plugins to extend the functionality of AWSume to your needs.

There are various types of plugins you can write, and there is some boilerplate that you must follow when writing them.

## How To Make Plugins

These Plugins must be written in Python. AWSume's uses *Yapsy* as it's plugin manager.
The plugins must be placed in the `~/.aws/awsumePlugins/` directory. You must create two files for each plugin you make, `plugin_name.py` and `plugin_name.yapsy-plugin`. 
The contents of the `.yapsy-plugin` file should be:

```
[Core]
Name = plugin_name
Module = plugin_name.py

[Documentation]
Author = John Doe
Version = 0.0.0
Website = http://super-awsume-plugin.com/
Description = This plugin does something awsume.
```

The `plugin_name.py` file should contain:

``` python
from yapsy import IPlugin
from awsume import awsumepy

class SomePlugin(IPlugin):
    def function_name(self):
        #Do new things
        return someImportantData
```

It's always a good idea to import the `awsumepy` library when using plugins. Each plugin consists of a class with various function definitions. Each function definition has a list of arguments it takes and what should be returned from each function.

The function definition must match exactly what AWSume expects for the plugin to be fully functional. All plugins are called along-side their default counterparts.

When displaying information, always print to `sys.stderr`, so that the `stdout` is not interfered with. This is because the shell wrappers are reading from `stdout` and if you print there, it will disrupt the functionality of AWSume.

## Plugin Functions

 ### Add Arguments

- ***Function Name:*** `add_arguments_func`
- ***Arguments:***
  - `argParser` An `ArgumentParser` object from Python's *ArgParse* library
- This function simply adds arguments to AWSume's argument parser. To do so is very simple, you justhave to invoke Python's *ArgParse* `add_argument` function on the `argParser`.
- This function requires you to return that object for your changes to take place.
- This plugin will always be called along with the default, when available, to add arguments.

``` python
import argparse
from yapsy import IPlugin
from awsume import awsumepy

class SomePlugin(IPlugin.IPlugin):
    def add_arguments_func(self, awsumeArgParser):
        #new special flag
        awsumeArgParser.add_argument('-x', action='store_true', default=False,
                                     dest='special_flag',
                                     help='Trigger a special event')
        return awsumeArgParser
```

### Handle Arguments

- ***Function Name:*** `handle_arguments_func`
- ***Arguments:***
  - `arguments` What was returned from `add_arguments_func`
- This function is called to handle anything special that should happen when an argument is in acertain state.
- For instance, when the `-v` flag is passed, to display the version, the displaying of the versionis handled in the default `handle_arguments_func`. For any arguments you add, this is where you canhandle those arguments.
- This function does not return anything.

``` python
from __future__ import print_function
import sys, argparse
from yapsy import IPlugin
from awsume import awsumepy

class SomePlugin(IPlugin.IPlugin):
    def handle_arguments_func(self, arguments):
        awsumepy.handle_command_line_arguments(arguments)
        if arguments.special_flag:
            print("Special flag triggered!", file=sys.stderr)
            exit(0)
```

### Get Config Profile List

- ***Function Name:*** `get_config_profile_list_func`
- ***Arguments:***
  - `arguments` What was returned from `add_arguments_func`
  - `configFilePath` The path to the config file.
- This function returns a list of all config profiles in the format of an `OrderedDict`.
- The format to return is the format that Python's *ConfigParser* library returns when it reads anINI file. The OrderedDict contains a list of tuples. Each tuple consists of the profile name and thenan OrderedDict of the profile itself.
- Each profile looks something like this:

``` python
OrderedDict([('__name__', 'the-profile-name'), ('some_key', 'some_value')])
```

  - The return value as a whole would look something like this:

``` python
OrderedDict([('profile1', profile1), ('profile2', profile2)])
```

  - The function's return value will be added to the default's return values, so that AWSume is just looking through a bigger list of profiles.

``` python
from yapsy import IPlugin
from collections import OrderedDict
from awsume import awsumepy

class SomePlugin(IPlugin.IPlugin):
    def get_config_profile_list_func(self, configFilePath):
        profile = OrderedDict([('__name__', 'my-profile'),
                               ('mfa_serial', 'arn:aws:iam::ACCOUNT_ID:mfa/Name'),
                               ('region', 'us-east-1')])
        profiles = OrderedDict()
        profiles['my-profile'] = profile
        return profiles
```

### Get Credentials Profile List

- ***Function Name:*** `get_credentials_profile_list_func`
- ***Arguments:***
  - `arguments` What was returned from `add_arguments_func`
  - `credentialsFilePath` The path to the credentials file
- This function returns a list of all credentials profiles in the format of an `OrderedDict`.
- The format to return is the format that Python's *ConfigParser* library returns when it reads an INI file. The OrderedDict contains a list of tuples. Each tuple consists of the profile name and then an OrderedDict of the profile itself.
- The list of profiles would be constructed similarly to the `get_config_profile_list_func` function.

``` python
from yapsy import IPlugin
from collections import OrderedDict
from awsume import awsumepy

class SomePlugin(IPlugin.IPlugin):
    def get_credentials_profile_list_func(self, configFilePath):
        profile = OrderedDict([('__name__', 'my-source'),
                               ('aws_access_key_id', 'SOMEACCESSKEYID'),
                               ('aws_secret_access_key', 'SOMESECRETACCESSKEY')])
        profiles = OrderedDict()
        profiles['my-source'] = profile
        return profiles
```

### Get Config Profile

- ***Function Name:*** `get_config_profile_func`
- ***Arguments:***
  - `configProfileList` What was returned from `get_config_profile_list_func`
  - `arguments` What was returned from `add_arguments_func`
- This function returns the config profile that will be used in assuming the role or setting the session. This could be either a role profile with a `role_arn` and a `source_profile`, or it could just be a user profile.
- AWSume will call each registered function until it is able to find a config profile. If the default function returns a config profile, the plugin function will not be called. For any case in which your plugin function doesn't find a config profile to return, always return an empty `OrderedDict()` for best compatibility.

``` python
from yapsy import IPlugin
from collections import OrderedDict
from awsume import awsumepy

class SomePlugin(IPlugin.IPlugin):
    def get_config_profile_func(self, configFilePath):
        profile = OrderedDict([('__name__', 'my-profile'),
                               ('mfa_serial', 'arn:aws:iam::ACCOUNT_ID:mfa/Name'),
                               ('region', 'us-east-1')])
        return profile
```

### Get Credentials Profile

- ***Function Name:*** `get_credentials_profile_func`
- ***Arguments:***
  - `credentialsProfileList` What was returned from `get_config_profile_list_func`
  - `configProfile` What was returned from `get_config_profile_func`
  - `arguments` What was returned from `add_arguments_func`
  - `credentialsFilePath` The path to the credentials file
- This function returns the credentials profile that will be used in assuming the role or setting the session. This is the profile that contains the `aws_access_key_id` and the `aws_secret_access_key`.
- AWSume will call each registered function until it is able to find a credentials profile. If the default function returns a credentials profile, the plugin function will not be called. For any case in which your plugin function doesn't find a credentials profile to return, always return an empty `OrderedDict()` for best compatibility.

``` python
from yapsy import IPlugin
from collections import OrderedDict
from awsume import awsumepy

class SomePlugin(IPlugin.IPlugin):
    def get_credentials_profile_func(self, configFilePath):
        profile = OrderedDict([('__name__', 'my-source'),
                               ('aws_access_key_id', 'SOMEACCESSKEYID'),
                               ('aws_secret_access_key', 'SOMESECRETACCESSKEY')])
        return profile
```

### Handle Profiles

- ***Function Name:*** `handle_profiles_func`
- ***Arguments:***
  - `configProfile` What was returned from `get_config_profile_func`
  - `credentialsProfile` What was returned from `get_credentials_profile_func`
  - `arguments` What was returned from `add_arguments_func`
- This function handles any special cases that the profiles may be in. The default function validates these profiles to make sure they'll work.
- This profile does not return anything.

``` python
from yapsy import IPlugin
from collections import OrderedDict
from awsume import awsumepy

class SomePlugin(IPlugin.IPlugin):
    def handle_profiles_func(self, configProfile, credentialsProfile, commandLineArguments):
        if configProfile is special and credentialsProfile is special:
            do_something_special()
            exit(0)
```

### Get User Credentials

- ***Function Name:*** `get_user_credentials_func`
- ***Arguments:***
  - `configProfile` What was returned from `get_config_profile_func`
  - `credentialsProfile` What was returned from `get_credentials_profile_func`
  - `userSession` The session returned from the previous `get_user_credentials_func` call
  - `cachePath` The path that AWSume will write the cache'd credentials to
  - `arguments` What was returned from `add_arguments_func`
- This function handles the actual `get_session_token` call to AWS to get the user credentials.
- This function returns those credentials that will be used in assuming the role or setting the session.
- This function will run with the state of the previous `get_user_credentials_func` function.
- If your implementation doesn't find anything, instead of returning `None`, you should return the previous `userSession` credentials

``` python
from yapsy import IPlugin
from collections import OrderedDict
from awsume import awsumepy

class SomePlugin(IPlugin.IPlugin):
    def get_user_credentials_func(configSection, credentialsSection, userSession, cachePath, arguments):
        session = make_custom_aws_call( ... )
        if not session:
            return userSession #if the call didn't return anything, return the previous state
        # format the session into an object that is compatible with AWSume
        awsumepy.create_awsume_session(session, configSection)
    return session
```

def get_user_credentials(configSection, credentialsSection, userSession, cachePath, arguments):

### Handle Getting Role

- ***Function Name:*** `handle_getting_role_func`
- ***Arguments:***
  - `configProfile` What was returned from `get_config_profile_func`
  - `credentialsProfile` What was returned from `get_credentials_profile_func`
  - `userSession` What was returned from the `get_user_session
  - `roleSession` The session returned from the previous `handle_getting_role_func` call
  - `cachePath` The path that AWSume will write the cache'd credentials to
  - `arguments` What was returned from `add_arguments_func`
- This function handles the actual `assume_role` call to AWS that gets the role credentials.
- It should verify that the configSection is actually a role with `awsumepy.is_role_profile(configSection)`. If it is not a role, then it should return `None`
- This returns those credentidals that will be used in assuming the role.
- This function will run with the state of the previous `handle_getting_role_func`
- If your implementation doesn't find anything, instead of returning `None`, you should return the previous `roleSession` credentials

``` python
from yapsy import IPlugin
from collections import OrderedDict
from awsume import awsumepy

class SomePlugin(IPlugin.IPlugin):
    def handle_getting_role_credentials_func(configSection,
                                             credentialsSection,
                                             userSession,
                                             roleSession,
                                             arguments):
        if not awsumepy.is_role_profile(configSection):
            return None
        roleSession = make_custom_aws_call( ... )
        #if the call didn't return anything, return the previous state
        if not roleSession:
            return roleSession
        # format the session into an object that is compatible with AWSume
        awsumepy.create_awsume_session(roleSession, configSection)
    return roleSession
```

### Post AWSume

- ***Function Name:*** `post_awsume_func`
- ***Arguments:***
  - `configProfileList` What was returned from `get_config_profile_list_func`
  - `credentialsProfileList` What was returned from `get_config_profile_list_func`
  - `configSection` What was returned from `get_config_profile_func`
  - `credentialsSection` What was returned from `get_credentials_profile_func`
  - `sessionToUse` The session that will be sent into the environment variables
  - `arguments` What was returned from `add_arguments_func`
- This function is used to handle anything you may need to handle after AWSume runs.
- Note: Since this is still in the Python space of AWSume, actual environment variables have not been set. However, you can access that data through `sessionToUse`.

``` python
from yapsy import IPlugin
from collections import OrderedDict
from awsume import awsumepy

class SomePlugin(IPlugin.IPlugin):
    def post_awsume_func(configProfileList,
                         credentialsProfileList,.
                         configSection,
                         credentialsSection,
                         userSession,
                         roleSession,
                         arguments):
        print("Congrats! You've finished running AWSume!", file=sys.stderr)
    return roleSession
```
