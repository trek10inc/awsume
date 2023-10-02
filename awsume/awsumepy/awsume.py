from typing import Union

import boto3

from .app import Awsume

cached_awsume_app_object = None


def awsume(profile_name: str = None, *args: list, **kwargs: dict) -> Union[boto3.Session, dict]:
    cli_arguments = list(args) if args is not None else []

    for key, value in kwargs.items():
        newkey = '--' + key.replace('_', '-')
        cli_arguments.append(str(newkey))
        if not isinstance(value, bool):
            cli_arguments.append(str(value))

    global cached_awsume_app_object  # this prevents numerous unique objects, such as AWS SDK, from being created
    if cached_awsume_app_object:
        app = cached_awsume_app_object
    else:
        app = Awsume(is_interactive=False)
        cached_awsume_app_object = app
    return app.run([profile_name] + cli_arguments)
