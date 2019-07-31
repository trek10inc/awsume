import os
import sys
import argparse
import difflib
import json
import logging
import pluggy
import colorama
from pathlib import Path

from . lib.profile import aggregate_profiles
from . lib.config_management import load_config
from . lib.aws_files import get_aws_files
from . lib.exceptions import ProfileNotFoundError, InvalidProfileError, UserAuthenticationError, RoleAuthenticationError
from . lib.logger import logger
from . lib.safe_print import safe_print
from . lib import constants
from . lib import saml as saml
from . lib import aws as aws_lib
from . import hookspec
from . import default_plugins


class Awsume(object):
    def __init__(self):
        logger.debug('Initalizing app')
        self.plugin_manager = self.get_plugin_manager()
        self.config = load_config()
        colorama.init(autoreset=True)


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
            formatter_class=lambda prog: (argparse.RawDescriptionHelpFormatter(prog, max_help_position=80, width=80)), # pragma: no cover
        )
        self.plugin_manager.hook.pre_add_arguments(
            config=self.config,
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
        if args.list_plugins:
            for plugin_name, _ in self.plugin_manager.list_name_plugin():
                if 'default_plugins' not in plugin_name:
                    safe_print(plugin_name, color=colorama.Fore.LIGHTCYAN_EX)
            exit(0)
        self.plugin_manager.hook.post_add_arguments(
            config=self.config,
            arguments=args,
            parser=argument_parser,
        )
        args.system_arguments = system_arguments
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


    def get_saml_credentials(self, args: argparse.Namespace) -> dict:
        assertion = self.plugin_manager.hook.get_credentials_with_saml(
            config=self.config,
            arguments=args,
        )
        assertion = next((_ for _ in assertion if _), None) # pragma: no cover
        if not assertion:
            safe_print('No assertion to use!', colorama.Fore.RED)
            exit(1)
        roles = saml.parse_assertion(assertion)
        if not roles:
            safe_print('No roles found in the saml assertion', colorama.Fore.RED)
            exit(1)
        role_arn = None
        principal_arn = None
        role_duration = args.role_duration or int(self.config.get('role-duration', '0'))

        if len(roles) > 1:
            if args.role_arn:
                choice = difflib.get_close_matches(args.role_arn, roles, cutoff=0)[0]
                safe_print('Closest match: {}'.format(choice))
            else:
                for index, choice in enumerate(roles):
                    safe_print('{}) {}'.format(index, choice), color=colorama.Fore.LIGHTYELLOW_EX)
                safe_print('Which role do you want to assume? > ', end='', color=colorama.Fore.LIGHTCYAN_EX)
                response = input()
                if response.isnumeric():
                    choice = roles[int(response)]
                else:
                    choice = difflib.get_close_matches(response, roles, cutoff=0)[0]
            role_arn = choice.split(',')[1]
            principal_arn = choice.split(',')[0]
        else:
            role_arn = roles[0].split(',')[1]
            principal_arn = roles[0].split(',')[0]
        safe_print('Assuming role: {},{}'.format(principal_arn, role_arn), color=colorama.Fore.GREEN)
        credentials = aws_lib.assume_role_with_saml(
            role_arn,
            principal_arn,
            assertion,
            region=None,
            role_duration=role_duration,
        )
        return credentials


    def get_credentials(self, args: argparse.Namespace, profiles: dict) -> dict:
        logger.debug('Getting credentials')
        self.plugin_manager.hook.pre_get_credentials(
            config=self.config,
            arguments=args,
            profiles=profiles,
        )
        try:
            if args.json or not sys.stdin.isatty(): # piping/sending credentials to awsume directly
                logger.debug('Pulling credentials from {}'.format('json parameter' if args.json else 'stdin'))
                args.target_profile_name = 'json' if args.json else 'stdin'
                json_input = args.json if args.json else sys.stdin.read()
                try:
                    credentials = json.loads(json_input)
                    if 'Credentials' in credentials:
                        credentials = credentials['Credentials']
                except json.JSONDecodeError:
                    safe_print('Data is not valid json')
                    exit(1)
                credentials = [credentials]
            elif args.with_saml:
                logger.debug('Pulling credentials from saml')
                credentials = self.get_saml_credentials(args)
                credentials = [credentials]
            elif args.with_web_identity:
                logger.debug('Pulling credentials from web identity')
                credentials = self.plugin_manager.hook.get_credentials_with_web_identity(
                    config=self.config,
                    arguments=args,
                )
            else:
                logger.debug('Pulling credentials from default awsume flow')
                credentials = self.plugin_manager.hook.get_credentials(config=self.config, arguments=args, profiles=profiles)
        except ProfileNotFoundError as e:
            safe_print(e, colorama.Fore.RED)
            logger.debug('', exc_info=True)
            self.plugin_manager.hook.catch_profile_not_found_exception(config=self.config, arguments=args, profiles=profiles, error=e)
            exit(1)
        except InvalidProfileError as e:
            safe_print(e, colorama.Fore.RED)
            logger.debug('', exc_info=True)
            self.plugin_manager.hook.catch_invalid_profile_exception(config=self.config, arguments=args, profiles=profiles, error=e)
            exit(1)
        except UserAuthenticationError as e:
            safe_print(e, colorama.Fore.RED)
            logger.debug('', exc_info=True)
            self.plugin_manager.hook.catch_user_authentication_error(config=self.config, arguments=args, profiles=profiles, error=e)
            exit(1)
        except RoleAuthenticationError as e:
            safe_print(e, colorama.Fore.RED)
            logger.debug('', exc_info=True)
            self.plugin_manager.hook.catch_role_authentication_error(config=self.config, arguments=args, profiles=profiles, error=e)
            exit(1)
        credentials = next((_ for _ in credentials if _), {}) # pragma: no cover
        self.plugin_manager.hook.post_get_credentials(
            config=self.config,
            arguments=args,
            profiles=profiles,
            credentials=credentials,
        )
        if not credentials:
            safe_print('No credentials to awsume', colorama.Fore.RED)
            exit(1)
        return credentials


    def export_data(self, awsume_flag: str, awsume_list: list):
        logger.debug('Exporting data')
        print(awsume_flag)
        print(' '.join(awsume_list))


    def run(self, system_arguments: list):
        result = self.plugin_manager.list_name_plugin()
        args = self.parse_args(system_arguments)
        profiles = self.get_profiles(args)
        credentials = self.get_credentials(args, profiles)

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
