# AWS External ID

We recommend reading the documentation on external ID's [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html).

An external ID can be provided to awsume in the following ways, following priority:

1. The `--external-id` flag
2. The target profile's `external_id` property
