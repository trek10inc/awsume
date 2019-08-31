# Config

Awsume's configuration file can be found at `~/.awsume/config.yaml`.

## Properties

There are a few configuration properties found in awsume's config:

```yaml
colors: true
fuzzy-match: true
role-duration: 0
region: us-west-2
```

- **colors** You can enable to disable adding colors to awsume's output. This is disabled on Windows machines.
- **fuzzy-match** You can enable to disable fuzzy-matching the given profile if the given profile is not found. See more about it [here](../advanced/fuzzy-matching)
- **role-duration** You can set a default role duration to awsume. _Note: If you specify a role duration that is greater than the maximum configured for that role, awsume will fail to assume the role. See how this impacts awsume [here](../advanced/role-duration)
- **region** You can specify a default region. See how this impacts awsume [here](../advanced/region)


## Modifying Config

You can use the `awsume --config` command to modify the config.

To configure awsume, you can edit the file manually or you can make use of the `--config` flag like this:

```
awsume --config set <key> <value> <value> <value>
```

```
awsume --config set role-duration 43200
```

Or you can reset to the default value with:

```
awsume --config reset role-duration
```

You can delete a value with:

```
awsume --config clear role-duration
```

And you can get complex with your config like this:

```yaml
# awsume --config set a.b.c x '{"hello":"world"}' 1 '"2"'
a:
  b:
    c:
     - 'x'
     - hello: world
     - 1
     - '2'
```

For each value, if it can be parsed as JSON, it will be. Otherwise it will be a string.

If you only provide one value, it will set the key to that value directly, without nesting it in an array, as follows:

```yaml
# awsume --config set a.b.c x
a:
  b:
    c: x
```

## Notes

Note that you can provide any data to awsume's config you want (it doesn't mean that anything will happen).

If you are a plugin developer, you can utilize awsume's global configuration to manage your plugin's configuration. **We recommend nesting your configuration under a top-level key (to not interfere with any other plugins or future configuration)**. For instance, the [awsume console plugin](https://github.com/trek10inc/awsume-console-plugin) stores its configuration under a top-level `console` key, like this:

```yaml
colors: true
fuzzy-match: true
role-duration: 0
region: us-west-2
console:
  browser_command: '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --user-data-dir=/tmp/{profile} "{url}" --no-first-run'
```
