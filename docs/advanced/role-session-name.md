# AWS Role Session Name

The AWS region can be provided to awsume in a number of ways, following this priority:

1. The `--session-name` flag
2. The profile's `role_session_name` property
3. Awsume's global configuraiton property (`role-session-name`)
4. If none of the above are present, the profile name will be used as the role session name
