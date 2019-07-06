import os
import sys
import argparse
import json
import logging
import pluggy
import colorama
from colorama import init, deinit
from pathlib import Path

from . lib.profile import aggregate_profiles
from . lib.config_management import load_config
from . lib.aws_files import get_aws_files
from . lib.exceptions import ProfileNotFoundError, InvalidProfileError, UserAuthenticationError, RoleAuthenticationError
from . lib.logger import logger
from . lib.safe_print import safe_print
from . lib import constants
from . import hookspec
from . import default_plugins


class Awsume(object):
    def __init__(self):
        self.plugin_manager = self.get_plugin_manager()
        self.config = load_config()
        init(autoreset=True)
        if not self.config.get('colors') == 'true':
            deinit()


    def get_plugin_manager(self) -> pluggy.PluginManager:
        logger.debug('Creating plugin manager')
        pm = pluggy.PluginManager('awsume')
        pm.add_hookspecs(hookspec)
        logger.debug('Loading plugins')
        pm.register(default_plugins)
        pm.load_setuptools_entrypoints('awsume')
        return pm


    def parse_args(self, system_arguments: list) -> argparse.Namespace:
        logger.debug('Gathering arguments')
        epilog = """Thank you for using AWSume! Check us out at https://trek10.com"""
        description="""Awsume - A cli that makes using AWS IAM credentials easy"""
        argument_parser = argparse.ArgumentParser(
            prog='awsume',
            description=description,
            epilog=epilog,
            formatter_class=lambda prog: (argparse.RawDescriptionHelpFormatter(prog, max_help_position=80, width=80)),
        )
        self.plugin_manager.hook.add_arguments(
            config=self.config,
            parser=argument_parser,
        )
        logger.debug('Parsing arguments')
        args = argument_parser.parse_args(system_arguments[1:])
        logger.debug('Handling arguments')
        if args.refresh_autocomplete:
            autocomplete_file = Path('~/.awsume/autocomplete.json').expanduser()
            result = self.plugin_manager.hook.get_profile_names(
                config=self.config,
                arguments=args,
            )
            profile_names = [y for x in result for y in x]
            json.dump({'profile-names': profile_names}, open(autocomplete_file, 'w'))
            exit(0)
        self.plugin_manager.hook.post_add_arguments(
            config=self.config,
            arguments=args,
            parser=argument_parser,
        )
        return args


    def get_profiles(self, args: argparse.Namespace) -> dict:
        logger.debug('Gathering profiles')
        config_file, credentials_file = get_aws_files(args, self.config)
        self.plugin_manager.hook.pre_collect_aws_profiles(
            config=self.config,
            arguments=args,
            credentials_file=credentials_file,
            config_file=config_file,
        )
        aws_profiles_result = self.plugin_manager.hook.collect_aws_profiles(
            config=self.config,
            arguments=args,
            credentials_file=credentials_file,
            config_file=config_file,
        )
        profiles = aggregate_profiles(aws_profiles_result)
        self.plugin_manager.hook.post_collect_aws_profiles(
            config=self.config,
            arguments=args,
            profiles=profiles,
        )
        return profiles


    def get_credentials(self, args: argparse.Namespace, profiles: dict) -> dict:
        logger.debug('Getting credentials')
        try:
            result = self.plugin_manager.hook.assume_role(config=self.config, arguments=args, profiles=profiles)
        except ProfileNotFoundError as e:
            safe_print(e, colorama.Fore.RED)
            logger.debug('', exc_info=True)
            self.plugin_manager.hook.catch_profile_not_found_exception(config=self.config, arguments=args, profiles=profiles)
            exit(1)
        except InvalidProfileError as e:
            safe_print(e, colorama.Fore.RED)
            logger.debug('', exc_info=True)
            self.plugin_manager.hook.catch_invalid_profile_error(config=self.config, arguments=args, profiles=profiles)
            exit(1)
        except UserAuthenticationError as e:
            safe_print(e, colorama.Fore.RED)
            logger.debug('', exc_info=True)
            self.plugin_manager.hook.catch_user_authentication_error(config=self.config, arguments=args, profiles=profiles)
            exit(1)
        except RoleAuthenticationError as e:
            safe_print(e, colorama.Fore.RED)
            logger.debug('', exc_info=True)
            self.plugin_manager.hook.catch_role_authentication_error(config=self.config, arguments=args, profiles=profiles)
            exit(1)
        return result


    def export_data(self, awsume_flag: str, awsume_list: list):
        logger.debug('Exporting data')
        print(awsume_flag)
        print(' '.join(awsume_list))


    def run(self, system_arguments: list):
        args = self.parse_args(system_arguments)
        args.system_arguments = system_arguments
        profiles = self.get_profiles(args)

        self.plugin_manager.hook.pre_assume_role(
            config=self.config,
            arguments=args,
            profiles=profiles,
        )
        if args.with_saml:
            credentials = {}
        elif args.with_web_identity:
            credentials = {}
        else:
            assume_role_result = self.get_credentials(args, profiles)
            credentials = next(_ for _ in assume_role_result if _)
        self.plugin_manager.hook.post_assume_role(
            config=self.config,
            arguments=args,
            profiles=profiles,
            credentials=credentials,
        )
        if args.auto_refresh:
            self.export_data('Auto', [
                'autoawsume-{}'.format(args.target_profile_name),
                credentials.get('Region'),
                args.target_profile_name,
            ])
        else:
            self.export_data('Awsume', [
                str(credentials.get('AccessKeyId')),
                str(credentials.get('SecretAccessKey')),
                str(credentials.get('SessionToken')),
                str(credentials.get('Region')),
                str(args.target_profile_name),
            ])