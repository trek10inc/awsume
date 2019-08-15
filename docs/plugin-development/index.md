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
