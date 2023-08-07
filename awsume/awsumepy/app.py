import os
import sys
import argparse
import difflib
import json
import logging
import pluggy
import colorama
import boto3
from pathlib import Path

from . lib.autoawsume import create_autoawsume_profile
from ..autoawsume.process import kill, kill_autoawsume
from . lib.profile import aggregate_profiles, get_role_chain, get_profile_name
from . lib.config_management import load_config
from . lib.aws_files import get_aws_files, add_section, get_section
from . lib.profile import credentials_to_profile, is_mutable_profile
from . lib import exceptions
from . lib.logger import logger
from . lib.safe_print import safe_print
from . lib import constants
from . lib import saml as saml
from . lib import aws as aws_lib
from . import hookspec
from . import default_plugins


class Awsume(object):
    def __init__(self, is_interactive: bool = True):
        logger.debug('Initalizing app')
        self.plugin_manager = self.get_plugin_manager()
        self.config = load_config()
        self.config['is_interactive'] = is_interactive
        self.is_interactive = is_interactive
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
        args = argument_parser.parse_args(system_arguments)
        logger.debug('Handling arguments')
        if args.refresh_autocomplete:
            autocomplete_file = Path('~/.awsume/autocomplete.json').expanduser()
            result = self.plugin_manager.hook.get_profile_names(
                config=self.config,
                arguments=args,
            )
            profile_names = [y for x in result for y in x]
            json.dump({'profile-names': profile_names}, open(autocomplete_file, 'w'))
            raise exceptions.EarlyExit()
        if args.list_plugins:
            for plugin_name, _ in self.plugin_manager.list_name_plugin():
                if 'default_plugins' not in plugin_name:
                    safe_print(plugin_name, color=colorama.Fore.LIGHTCYAN_EX)
            raise exceptions.EarlyExit()
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


    def get_saml_credentials(self, args: argparse.Namespace, profiles: dict) -> dict:
        assertion = self.plugin_manager.hook.get_credentials_with_saml(
            config=self.config,
            arguments=args,
        )
        assertion = next((_ for _ in assertion if _), None) # pragma: no cover
        if not assertion:
            raise exceptions.SAMLAssertionNotFoundError('No assertion to use!')
        roles = saml.parse_assertion(assertion)
        if not roles:
            raise exceptions.SAMLAssertionMissingRoleError('No roles found in the saml assertion')
        role_arn = None
        principal_arn = None
        role_duration = args.role_duration or int(self.config.get('role-duration', '0'))

        if len(roles) > 1:
            if args.role_arn and args.principal_arn:
                principal_plus_role_arn = ','.join([args.principal_arn, args.role_arn])
                if self.config.get('fuzzy-match'):
                    choice = difflib.get_close_matches(principal_plus_role_arn, roles, cutoff=0)[0]
                    safe_print('Closest match: {}'.format(choice))
                else:
                    if principal_plus_role_arn not in roles:
                        raise exceptions.SAMLRoleNotFoundError(args.principal_arn, args.role_arn)
                    else:
                        choice = principal_plus_role_arn
            elif args.profile_name:
                profile_role_arn = profiles.get(args.profile_name, {}).get('role_arn')
                principal_arn = profiles.get(args.profile_name, {}).get('principal_arn')
                if profile_role_arn is None or principal_arn is None:
                    raise exceptions.InvalidProfileError(args.profile_name, 'both role_arn and principal_arn are necessary for saml profiles')
                principal_plus_profile_role_arn = ','.join([profile_role_arn, principal_arn])
                if principal_plus_profile_role_arn in roles:
                    choice = principal_plus_profile_role_arn
                else:
                    raise exceptions.SAMLRoleNotFoundError(principal_arn, profile_role_arn)
                safe_print('Match: {}'.format(choice))
            else:
                for index, choice in enumerate(roles):
                    safe_print('{}) {}'.format(index, choice), color=colorama.Fore.LIGHTYELLOW_EX)
                safe_print('Which role do you want to assume? > ', end='', color=colorama.Fore.LIGHTCYAN_EX)
                response = input()
                if response.isnumeric():
                    choice = roles[int(response)]
                else:
                    choice = difflib.get_close_matches(response, roles, cutoff=0)[0]
        else:
            choice = roles[0]
        for arn in choice.split(','):
            if 'role' in arn:
                role_arn = arn
            if 'saml-provider' in arn:
                principal_arn = arn
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
            if not args.auto_refresh and args.json: # sending credentials to awsume directly
                logger.debug('Pulling credentials from json parameter')
                args.target_profile_name = 'json'
                credentials = json.loads(args.json)
                if 'Credentials' in credentials:
                    credentials = credentials['Credentials']
            elif args.with_saml:
                logger.debug('Pulling credentials from saml')
                credentials = self.get_saml_credentials(args, profiles)
            elif args.with_web_identity:
                logger.debug('Pulling credentials from web identity')
                credentials = self.plugin_manager.hook.get_credentials_with_web_identity(
                    config=self.config,
                    arguments=args,
                )
            else:
                logger.debug('Pulling credentials from default awsume flow')
                credentials = self.plugin_manager.hook.get_credentials(config=self.config, arguments=args, profiles=profiles)
                credentials = next((_ for _ in credentials if _), {})
                if args.auto_refresh:
                    create_autoawsume_profile(self.config, args, profiles, credentials)
                    if self.config.get('is_interactive'):
                        logger.debug('Interactive execution, killing existing autoawsume processes')
                        kill_autoawsume()
        except exceptions.ProfileNotFoundError as e:
            self.plugin_manager.hook.catch_profile_not_found_exception(config=self.config, arguments=args, profiles=profiles, error=e)
            raise
        except exceptions.InvalidProfileError as e:
            self.plugin_manager.hook.catch_invalid_profile_exception(config=self.config, arguments=args, profiles=profiles, error=e)
            raise
        except exceptions.UserAuthenticationError as e:
            self.plugin_manager.hook.catch_user_authentication_error(config=self.config, arguments=args, profiles=profiles, error=e)
            raise
        except exceptions.RoleAuthenticationError as e:
            self.plugin_manager.hook.catch_role_authentication_error(config=self.config, arguments=args, profiles=profiles, error=e)
            raise
        if type(credentials) == list: # pragma: no cover
            credentials = next((_ for _ in credentials if _), {}) # pragma: no cover
        self.plugin_manager.hook.post_get_credentials(
            config=self.config,
            arguments=args,
            profiles=profiles,
            credentials=credentials,
        )
        if not credentials:
            safe_print('No credentials to awsume', colorama.Fore.RED)
            raise exceptions.NoCredentialsError()
        return credentials


    def export_data(self, arguments: argparse.Namespace, profiles: dict, credentials: dict, awsume_flag: str, awsume_list: list):
        logger.debug('Exporting data')
        if self.is_interactive:
            print(awsume_flag, end=' ')
            print(' '.join(awsume_list))
        session = aws_lib.get_session(
            aws_access_key_id=credentials.get('AccessKeyId'),
            aws_secret_access_key=credentials.get('SecretAccessKey'),
            aws_session_token=credentials.get('SessionToken'),
            profile_name=credentials.get('AwsProfile'),
            region_name=credentials.get('Region'),
        )
        if arguments.output_profile and not arguments.auto_refresh:
            if not is_mutable_profile(profiles, arguments.output_profile):
                raise exceptions.ImmutableProfileError(arguments.output_profile, 'not awsume-managed')
            _, credentials_file = get_aws_files(arguments, self.config)
            awsumed_profile = credentials_to_profile(credentials)
            if 'Expiration' in credentials:
                awsumed_profile['expiration'] = credentials['Expiration'].strftime('%Y-%m-%d %H:%M:%S')
            add_section(arguments.output_profile, awsumed_profile, credentials_file, True)
        session.awsume_credentials = credentials
        return session


    def run(self, system_arguments: list):
        try:
            args = self.parse_args(system_arguments)
            profiles = self.get_profiles(args)
            credentials = self.get_credentials(args, profiles)

            if args.auto_refresh:
                return self.export_data(args, profiles, credentials, 'Auto', [
                    str(args.output_profile or 'autoawsume-{}'.format(args.target_profile_name)),
                    str(credentials.get('Region')),
                    str(args.target_profile_name),
                ])
            else:
                return self.export_data(args, profiles, credentials, 'Awsume', [
                    str(credentials.get('AccessKeyId')),
                    str(credentials.get('SecretAccessKey')),
                    str(credentials.get('SessionToken')),
                    str(credentials.get('Region')),
                    str(args.target_profile_name),
                    str(credentials.get('AwsProfile')),
                    str(credentials['Expiration'].strftime('%Y-%m-%dT%H:%M:%S') if 'Expiration' in credentials else None),
                ])
        except exceptions.EarlyExit as err:
            logger.debug('', exc_info=True)
            logger.debug('EarlyExit exception raised, no more work to do')
            return err.data
        except exceptions.AwsumeException as e:
            logger.debug('', exc_info=True)
            if self.is_interactive:
                safe_print('Awsume error: {}'.format(e), color=colorama.Fore.RED)
                sys.exit(1)
            else:
                raise
