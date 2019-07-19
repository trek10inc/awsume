import pluggy
import argparse

hookspec = pluggy.HookspecMarker('awsume')


@hookspec
def pre_add_arguments(config: dict):
    """pre add_arguments hook"""

@hookspec
def add_arguments(config: dict, parser: argparse.ArgumentParser):
    """add argparse arguments to the parser, should try/except for conflicting arguments"""

@hookspec
def post_add_arguments(config: dict, arguments: argparse.Namespace, parser: argparse.ArgumentParser):
    """post add_arguments hook"""



@hookspec
def pre_collect_aws_profiles(config: dict, arguments: argparse.Namespace, credentials_file: str, config_file: str):
    """"""

@hookspec
def collect_aws_profiles(config: dict, arguments: argparse.Namespace, credentials_file: str, config_file: str):
    """"""

@hookspec
def post_collect_aws_profiles(config: dict, arguments: argparse.Namespace, profiles: dict):
    """"""



@hookspec
def pre_get_credentials(config: dict, arguments: argparse.Namespace, profiles: dict):
    """"""

@hookspec
def get_credentials(config: dict, arguments: argparse.Namespace, profiles: dict):
    """"""

@hookspec
def get_credentials_with_saml(config: dict, arguments: argparse.Namespace):
    """"""

@hookspec
def get_credentials_with_web_identity(config: dict, arguments: argparse.Namespace):
    """"""

@hookspec
def post_get_credentials(config: dict, arguments: argparse.Namespace, profiles: dict, credentials: dict):
    """"""



@hookspec
def catch_profile_not_found_exception(config: dict, arguments: argparse.Namespace, profiles: dict, error: Exception):
    """"""

@hookspec
def catch_invalid_profile_exception(config: dict, arguments: argparse.Namespace, profiles: dict, error: Exception):
    """"""

@hookspec
def catch_user_authentication_error(config: dict, arguments: argparse.Namespace, profiles: dict, error: Exception):
    """"""

@hookspec
def catch_role_authentication_error(config: dict, arguments: argparse.Namespace, profiles: dict, error: Exception):
    """"""



@hookspec
def get_profile_names(config: dict, arguments: argparse.Namespace):
    """"""
