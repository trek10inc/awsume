# Plugins Introduction

You can make your own plugins to extend awsume's capabilities. Awsume uses [pluggy](https://pluggy.readthedocs.io/en/latest/) as a plugin manager. You can view our plugin starting point [here](https://github.com/trek10inc/awsume-plugin-example).

A plugin is a collection of methods. These methods are hooked into awsume's execution to extend it's functionality however you'd like. Awsume's core is actually composed of a bunch of these plugin methods. Check out the pluggy documentation to learn more about how the plugin system functions.

## Hookspecs

Awsume defines the following hookspecs, each with a `pre_` and `post_` hookspec so you can handle your plugin before and after each step in awsume's execution:

- `add_arguments`
- `collect_profiles`
- `get_credentials` (with extra `get_credentials_with_saml` and `get_credentials_with_web_identity`)
- `get_profile_names`

Awsume also defines the following hookspecs to handle your plugin in the event of an error:

- `catch_profile_not_found_exception`
- `catch_invalid_profile_exception`
- `catch_user_authentication_error`
- `catch_role_authentication_error`

## Calling Your Hooks

Awsume will call your plugin's hooks with the arguments specified in the hookspecs. You can see the various types of methods in the next pages of the documentation. You'll notice that a `config` variable is passed into almost all of the hook methods. You can read more about that [here](../general/usage.html#config).

## Common Arguments

There are a couple of common arguments to the hooks you can define: `arguments` and `config`.

### Arguments

Arguments is an `argparse.Namespace` containing the parsed command-line arguments. It's properties depend on the plugins you have installed, and the version of awsume you're running. This is the value returned from the `argparse.ArgumentParser` `parse_args` function. You can see all of the arguments by running `awsume -h`, or all of the default arguments [here](../general/usage).

### Config

Awsume's global configuration is supplied through the `config` argument. This is of the type `dict` and contains all the values from awsume's configuration. See more about that [here](../general/config).

An additional property is added to the config at runtime: `is_interactive`. This will be true for all invocations of awsume from the CLI. It will be false for any invocations from the `awsume.awsumepy.awsume` method call. See more about that [here](../advanced/non-interactive-awsume).
