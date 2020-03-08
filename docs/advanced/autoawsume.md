# Autoawsume

When you installed awsume, you may have noticed you also got an `autoawsume` command. This is a helper for awsume to automatically refresh role credentials.

To start auto-refreshing credentials, use the `-a`/`--auto-refresh` flag. This will tell awsume to spin off `autoawsume` in the background to handle refreshing those credentials. Instead of putting your credentials into your environment variables, it'll create a new profile in your credentials file prefixed with `autoawsume-`. It will also export the `AWS_PROFILE` and `AWS_DEFAULT_PROFILE` environment variables to point to the newly created profile.

If you use the `-o`/`--output-profile` flag, you can instead use a named profile (without the `autoawsume-` prefix) to store autoawsume'd credentials. With this, you could run the following command to enable auto-refreshed to be used by default among all shells on your machine:

```sh
awsume dev-admin -a -o default
```

_Note: Awsume will not overwrite an existing profile that is not managed by awsume (noted by the `manager = awsume` property)._

Autoawsume will look for when the earliest expiring profile will expire and wait until then, when it will re-execute awsume to refresh the credentials in the background, so you don't have to worry about needing to re-awsume your profile's credentials. It will continue to repeat this process until it cannot refresh credentials anymore (either the source_profile credentials expired or the user has requested to stop autoawsume with an `awsume -k`).
