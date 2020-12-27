from typing import Union
import boto3
from . app import Awsume


def awsume(profile_name: str = None, *args: list, **kwargs: dict) -> Union[boto3.Session, dict]:
    cli_arguments = list(args) if args is not None else []

    for key, value in kwargs.items():
        newkey = '--' + key.replace('_', '-')
        cli_arguments.append(str(newkey))
        if not isinstance(value, bool):
            cli_arguments.append(str(value))

    app = Awsume(is_interactive=False)
    return app.run([profile_name] + cli_arguments)
