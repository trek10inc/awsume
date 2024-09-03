# AWS Role Duration

If awsume is provided with a nonzero role duration, it will send that value to the `assume_role` call. If you don't want a role duration to be send to that call, specify a role duration of 0.

Using a custom role duration, you can get credentials for as little as 15 minutes or as long as 12 hours.

Where this can be a danger is that the default role duration for all roles is 1 hour. If you request role credentials for longer than the configured maximum, the `assume_role` call will fail entirely.

A role duration can be provided to awsume in the following ways, following priority:

1. The `--role-duration` flag
2. The target profile's `duration_seconds` property
3. Awsume's global configuration `role-duration` property
