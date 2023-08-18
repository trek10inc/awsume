import argparse
import pytest
from io import StringIO
from unittest.mock import MagicMock, patch
from awsume.awsumepy import default_plugins
from awsume.awsumepy.lib import exceptions, autoawsume


def generate_namespace_with_defaults(
        session_tags=None,
        region=None,
        source_profile=None,
        auto_refresh=None,
        clean=None,
        version=None,
        unset_variables=None,
        config=None,
        kill=None,
        with_saml=None,
        principal_arn=None,
        profile_name=None,
        **kwargs
) -> argparse.Namespace:
    return argparse.Namespace(
        session_tags=session_tags,
        region=region,
        source_profile=source_profile,
        auto_refresh=auto_refresh,
        clean=clean,
        version=version,
        unset_variables=unset_variables,
        config=config,
        kill=kill,
        with_saml=with_saml,
        principal_arn=principal_arn,
        profile_name=profile_name,
        **kwargs
    )


def test_custom_duration_argument_type():
    assert default_plugins.custom_duration_argument_type('43200') == 43200


def test_custom_duration_argument_type_less():
    with pytest.raises(argparse.ArgumentTypeError):
        default_plugins.custom_duration_argument_type('-1')


def test_add_arguments():
    parser = argparse.ArgumentParser()
    default_plugins.add_arguments({}, parser)
    parser.parse_args([])


@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_role_arn_no_auto_refresh(safe_print: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        role_arn=True,
        auto_refresh=True,
        version=False,
        unset_variables=False,
        config=False,
        kill=False,
        profile_name=None,
        clean=False,
        output_profile=None,
    )
    parser = argparse.ArgumentParser()
    with pytest.raises(exceptions.ValidationException):
        default_plugins.post_add_arguments(config, arguments, parser)


@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdout', new_callable=StringIO)
@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_version(safe_print: MagicMock, stdout: MagicMock, stderr: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        role_arn=False,
        auto_refresh=False,
        version=True,
        unset_variables=False,
        config=False,
        kill=False,
        profile_name=None,
        clean=False,
        output_profile=None,
    )
    parser = argparse.ArgumentParser()
    with pytest.raises(exceptions.EarlyExit):
        default_plugins.post_add_arguments(config, arguments, parser)


@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdout', new_callable=StringIO)
@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_unset_variables(safe_print: MagicMock, stdout: MagicMock, stderr: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        role_arn=False,
        auto_refresh=False,
        version=False,
        unset_variables=True,
        config=False,
        kill=False,
        profile_name=None,
        clean=False,
        output_profile=None,
    )
    parser = argparse.ArgumentParser()
    with pytest.raises(exceptions.EarlyExit):
        default_plugins.post_add_arguments(config, arguments, parser)


@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdout', new_callable=StringIO)
@patch.object(default_plugins, 'config_lib')
@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_config(safe_print: MagicMock, config_lib: MagicMock, stdout: MagicMock, stderr: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        role_arn=False,
        auto_refresh=False,
        version=False,
        unset_variables=False,
        config=['clear', 'role-duration'],
        kill=False,
        profile_name=None,
        clean=False,
        output_profile=None,
    )
    parser = argparse.ArgumentParser()
    with pytest.raises(exceptions.EarlyExit):
        default_plugins.post_add_arguments(config, arguments, parser)
    config_lib.handle_config.assert_called_with(arguments.config)


@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdout', new_callable=StringIO)
@patch.object(default_plugins, 'kill')
@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_kill(safe_print: MagicMock, kill: MagicMock, stdout: MagicMock, stderr: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        role_arn=False,
        auto_refresh=False,
        version=False,
        unset_variables=False,
        config=None,
        kill=True,
        profile_name=None,
        clean=False,
        output_profile=None,
    )
    parser = argparse.ArgumentParser()
    with pytest.raises(exceptions.EarlyExit):
        default_plugins.post_add_arguments(config, arguments, parser)
    kill.assert_called_with(arguments)


@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_role_arn_short(safe_print: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_arn='123123123123:myrole',
        auto_refresh=False,
        version=False,
        unset_variables=False,
        config=None,
        kill=False,
        profile_name=None,
        clean=False,
        output_profile=None,
        with_saml=False,
        principal_arn=None,
    )
    parser = argparse.ArgumentParser()
    default_plugins.post_add_arguments(config, arguments, parser)
    assert arguments.role_arn == 'arn:aws:iam::123123123123:role/myrole'


@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdout', new_callable=StringIO)
@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_role_arn_short_bad_id(safe_print: MagicMock, stdout: MagicMock, stderr: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        role_arn='notanid:myrole',
        auto_refresh=False,
        version=False,
        unset_variables=False,
        config=None,
        kill=False,
        profile_name=None,
        clean=False,
        output_profile=None,
        with_saml=False,
        principal_arn=None,
    )
    parser = argparse.ArgumentParser()
    with pytest.raises(SystemExit):
        default_plugins.post_add_arguments(config, arguments, parser)


@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdout', new_callable=StringIO)
@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_role_arn_short_bad_number_parts(safe_print: MagicMock, stdout: MagicMock, stderr: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        role_arn='notanid:myrole:other',
        auto_refresh=False,
        version=False,
        unset_variables=False,
        config=None,
        kill=False,
        profile_name=None,
        clean=False,
        output_profile=None,
        with_saml=False,
        principal_arn=None,
    )
    parser = argparse.ArgumentParser()
    with pytest.raises(SystemExit):
        default_plugins.post_add_arguments(config, arguments, parser)


@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_role_arn_explicit(safe_print: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_arn='arn:aws:iam::123123123123:role/myrole',
        auto_refresh=False,
        version=False,
        unset_variables=False,
        config=None,
        kill=False,
        profile_name=None,
        clean=False,
        output_profile=None,
        with_saml=False,
        principal_arn=None,
    )
    parser = argparse.ArgumentParser()
    default_plugins.post_add_arguments(config, arguments, parser)


@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_set_target_profile_name(safe_print: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_arn=None,
        auto_refresh=False,
        version=False,
        unset_variables=False,
        config=None,
        kill=False,
        profile_name='profile',
        clean=False,
        output_profile=None,
        with_saml=False,
        principal_arn=None,
    )
    parser = argparse.ArgumentParser()
    default_plugins.post_add_arguments(config, arguments, parser)
    assert arguments.target_profile_name == 'profile'


@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_set_target_profile_name_default(safe_print: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_arn=None,
        auto_refresh=False,
        version=False,
        unset_variables=False,
        config=None,
        kill=False,
        profile_name=None,
        clean=False,
        output_profile=None,
        with_saml=False,
        principal_arn=None,
    )
    parser = argparse.ArgumentParser()
    default_plugins.post_add_arguments(config, arguments, parser)
    assert arguments.target_profile_name == 'default'


@patch.object(default_plugins, 'safe_print')
def test_post_add_arguments_set_target_profile_name_role_arn(safe_print: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_arn='arn:aws:iam::123123123123:role/myrole',
        auto_refresh=False,
        version=False,
        unset_variables=False,
        config=None,
        kill=False,
        profile_name=None,
        clean=False,
        output_profile=None,
        with_saml=False,
        principal_arn=None,
    )
    parser = argparse.ArgumentParser()
    default_plugins.post_add_arguments(config, arguments, parser)
    assert arguments.target_profile_name == 'arn:aws:iam::123123123123:role/myrole'


@patch.object(default_plugins, 'aws_files_lib')
def test_collect_aws_profiles(aws_files: MagicMock):
    credentials_profiles = {
        'admin': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }
    config_profiles = {
        'profile admin': {
            'region': 'us-east-1',
        },
        'profile other': {
            'region': 'us-east-1',
        },
    }
    aws_files.read_aws_file.side_effect = [credentials_profiles, config_profiles]
    args = argparse.Namespace()
    config = {}
    result = default_plugins.collect_aws_profiles(config, args, 'credentials/file', 'config/file')
    assert result == {
        'admin': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'region': 'us-east-1',
        },
        'other': {
            'region': 'us-east-1',
        },
    }


@patch.object(default_plugins, 'profile_lib')
def test_post_collect_aws_profiles(profile_lib: MagicMock):
    profiles = {
        'admin': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }
    args = argparse.Namespace(list_profiles='list')
    config = {}
    with pytest.raises(exceptions.EarlyExit):
        default_plugins.post_collect_aws_profiles(config, args, profiles)
    profile_lib.list_profile_data.assert_called_with(profiles, False, config)


@patch.object(default_plugins, 'profile_lib')
def test_post_collect_aws_profiles_list_more(profile_lib: MagicMock):
    profiles = {
        'admin': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }
    args = argparse.Namespace(list_profiles='more')
    config = {}
    with pytest.raises(exceptions.EarlyExit):
        default_plugins.post_collect_aws_profiles(config, args, profiles)
    profile_lib.list_profile_data.assert_called_with(profiles, True, config)


@patch.object(default_plugins, 'profile_lib')
def test_post_collect_aws_profiles_list_non_interactive(profile_lib: MagicMock):
    profiles = {
        'admin': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }
    args = argparse.Namespace(list_profiles='list')
    config = {
        'is_interactive': False,
    }
    with pytest.raises(exceptions.EarlyExit) as early_exit_exception:
        default_plugins.post_collect_aws_profiles(config, args, profiles)
    assert early_exit_exception.value.data == {'profiles': profile_lib.list_profile_data.return_value}
    profile_lib.list_profile_data.assert_called_with(profiles, False, config)


@patch.object(default_plugins, 'profile_lib')
def test_post_collect_aws_profiles_no_list(profile_lib: MagicMock):
    profiles = {
        'admin': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }
    args = argparse.Namespace(list_profiles=False)
    config = {}
    default_plugins.post_collect_aws_profiles(config, args, profiles)
    profile_lib.list_profile_data.assert_not_called()


@patch.object(default_plugins, 'profile_lib')
@patch.object(default_plugins, 'aws_lib')
def test_assume_role_from_cli(aws_lib: MagicMock, profile_lib: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_duration=None,
        session_name=None,
        source_profile=None,
        role_arn='myrolearn',
        external_id=None,
        mfa_token=None,
        force_refresh=False,
    )
    profiles = {}
    default_plugins.assume_role_from_cli(config, arguments, profiles)
    aws_lib.assume_role.assert_called_with(
        {}, arguments.role_arn, 'awsume-cli-role',
        region=profile_lib.get_region.return_value,
        external_id=arguments.external_id,
        role_duration=0,
        tags=None,
    )


@patch.object(default_plugins, 'profile_lib')
@patch.object(default_plugins, 'aws_lib')
def test_assume_role_from_cli_source_profile(aws_lib: MagicMock, profile_lib: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_duration=None,
        session_name=None,
        source_profile='mysource',
        role_arn='myrolearn',
        external_id=None,
        mfa_token='123123',
        force_refresh=False,
    )
    profiles = {
        'mysource': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'mfa_serial': 'mymfaserial',
        },
    }
    profile_lib.profile_to_credentials.return_value = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
    }
    default_plugins.assume_role_from_cli(config, arguments, profiles)
    aws_lib.get_session_token.assert_called_with(profile_lib.profile_to_credentials.return_value, region=profile_lib.get_region.return_value, mfa_serial='mymfaserial', mfa_token='123123', ignore_cache=False, duration_seconds=None)
    aws_lib.assume_role.assert_called_with(
        aws_lib.get_session_token.return_value,
        arguments.role_arn,
        'awsume-cli-role',
        region=profile_lib.get_region.return_value,
        external_id=arguments.external_id,
        role_duration=0,
        tags=None
    )


@patch.object(default_plugins, 'profile_lib')
@patch.object(default_plugins, 'aws_lib')
def test_assume_role_from_cli_source_profile_role_duration_mfa(aws_lib: MagicMock, profile_lib: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_duration='43200',
        session_name=None,
        source_profile='mysource',
        role_arn='myrolearn',
        external_id=None,
        mfa_token='123123',
        force_refresh=False,
    )
    profiles = {
        'mysource': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'mfa_serial': 'mymfaserial',
        },
    }
    profile_lib.profile_to_credentials.return_value = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
    }
    default_plugins.assume_role_from_cli(config, arguments, profiles)
    aws_lib.get_session_token.assert_not_called()
    aws_lib.assume_role.assert_called_with(
        profile_lib.profile_to_credentials.return_value,
        arguments.role_arn,
        'awsume-cli-role',
        region=profile_lib.get_region.return_value,
        external_id=arguments.external_id,
        role_duration='43200',
        mfa_serial='mymfaserial',
        mfa_token='123123',
        tags=None,
    )


@patch.object(default_plugins, 'profile_lib')
@patch.object(default_plugins, 'aws_lib')
def test_assume_role_from_cli_source_profile_role_duration_no_mfa(aws_lib: MagicMock, profile_lib: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_duration='43200',
        session_name=None,
        source_profile='mysource',
        role_arn='myrolearn',
        external_id=None,
        mfa_token=None,
        force_refresh=False,
    )
    profiles = {
        'mysource': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }
    profile_lib.profile_to_credentials.return_value = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
    }
    default_plugins.assume_role_from_cli(config, arguments, profiles)
    aws_lib.get_session_token.assert_not_called()
    aws_lib.assume_role.assert_called_with(
        profile_lib.profile_to_credentials.return_value,
        arguments.role_arn,
        'awsume-cli-role',
        region=profile_lib.get_region.return_value,
        external_id=arguments.external_id,
        role_duration='43200',
        tags=None,
    )


@patch.object(default_plugins, 'profile_lib')
@patch.object(default_plugins, 'aws_lib')
def test_assume_role_from_cli_source_profile_no_role_duration_mfa(aws_lib: MagicMock, profile_lib: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_duration=None,
        session_name=None,
        source_profile='mysource',
        role_arn='myrolearn',
        external_id=None,
        mfa_token='123123',
        force_refresh=False,
    )
    profiles = {
        'mysource': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'mfa_serial': 'mymfaserial',
        },
    }
    profile_lib.profile_to_credentials.return_value = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
    }
    default_plugins.assume_role_from_cli(config, arguments, profiles)
    aws_lib.get_session_token.assert_called_with(
        { 'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET' },
        region=profile_lib.get_region.return_value,
        mfa_serial='mymfaserial',
        mfa_token='123123',
        ignore_cache=False,
        duration_seconds=None,
    )
    aws_lib.assume_role.assert_called_with(
        aws_lib.get_session_token.return_value,
        arguments.role_arn,
        'awsume-cli-role',
        region=profile_lib.get_region.return_value,
        external_id=arguments.external_id,
        role_duration=0,
        tags=None,
    )


@patch.object(default_plugins, 'profile_lib')
@patch.object(default_plugins, 'aws_lib')
def test_assume_role_from_cli_source_profile_no_role_duration_no_mfa(aws_lib: MagicMock, profile_lib: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_duration=None,
        session_name=None,
        source_profile='mysource',
        role_arn='myrolearn',
        external_id=None,
        mfa_token=None,
        force_refresh=False,
    )
    profiles = {
        'mysource': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }
    profile_lib.profile_to_credentials.return_value = {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
    }
    default_plugins.assume_role_from_cli(config, arguments, profiles)
    aws_lib.get_session_token.assert_not_called()
    aws_lib.assume_role.assert_called_with(
        profile_lib.profile_to_credentials.return_value,
        arguments.role_arn,
        'awsume-cli-role',
        region=profile_lib.get_region.return_value,
        external_id=arguments.external_id,
        role_duration=0,
        tags=None,
    )


@patch.object(default_plugins, 'profile_lib')
@patch.object(default_plugins, 'aws_lib')
def test_assume_role_from_cli_source_profile_not_found(aws_lib: MagicMock, profile_lib: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        role_duration=None,
        session_name=None,
        source_profile='notfoundsource',
        role_arn='myrolearn',
        external_id=None,
        mfa_token='123123',
        force_refresh=False,
    )
    profiles = {
        'mysource': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'mfa_serial': 'mymfaserial',
        },
    }
    with pytest.raises(exceptions.ProfileNotFoundError):
        default_plugins.assume_role_from_cli(config, arguments, profiles)


@patch.object(autoawsume, 'create_autoawsume_profile')
@patch.object(default_plugins, 'aws_lib')
def test_get_credentials(aws_lib: MagicMock, create_autoawsume_profile: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        target_profile_name='role',
        external_id='myexternalid',
        role_duration=None,
        role_arn=None,
        session_name='mysessionname',
        mfa_token='123123',
        force_refresh=True,
        auto_refresh=False,
        region=None,
        output_profile=None,
    )
    profiles = {
        'role': {
            'role_arn': 'myrolearn',
            'source_profile': 'user',
        },
        'user': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'mfa_serial': 'mymfaserial',
        },
    }

    result = default_plugins.get_credentials(config, arguments, profiles)
    aws_lib.get_session_token.assert_called_with(
        { 'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': None, 'Region': None },
        region=None,
        mfa_serial='mymfaserial',
        mfa_token='123123',
        ignore_cache=True,
        duration_seconds=None,
    )
    aws_lib.assume_role.assert_called_with(
        aws_lib.get_session_token.return_value,
        'myrolearn',
        'mysessionname',
        region=None,
        external_id='myexternalid',
        role_duration=0,
        tags=None,
    )
    assert result == aws_lib.assume_role.return_value


@patch.object(autoawsume, 'create_autoawsume_profile')
@patch.object(default_plugins, 'aws_lib')
def test_get_credentials_auto_refresh(aws_lib: MagicMock, create_autoawsume_profile: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        target_profile_name='role',
        external_id='myexternalid',
        role_duration=None,
        role_arn=None,
        session_name='mysessionname',
        mfa_token='123123',
        force_refresh=True,
        auto_refresh=True,
        region=None,
        output_profile=None,
    )
    profiles = {
        'role': {
            'role_arn': 'myrolearn',
            'source_profile': 'user',
        },
        'user': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'mfa_serial': 'mymfaserial',
        },
    }
    aws_lib.assume_role.return_value = {
        'SourceExpiration': '2077-10-24',
    }

    result = default_plugins.get_credentials(config, arguments, profiles)
    aws_lib.get_session_token.assert_called_with(
        { 'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': None, 'Region': None },
        region=None,
        mfa_serial='mymfaserial',
        mfa_token='123123',
        ignore_cache=True,
        duration_seconds=None,
    )
    aws_lib.assume_role.assert_called_with(
        aws_lib.get_session_token.return_value,
        'myrolearn',
        'mysessionname',
        region=None,
        external_id='myexternalid',
        role_duration=0,
        tags=None
    )
    assert result == aws_lib.assume_role.return_value


@patch.object(autoawsume, 'create_autoawsume_profile')
@patch.object(default_plugins, 'aws_lib')
def test_get_credentials_role_duration(aws_lib: MagicMock, create_autoawsume_profile: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        target_profile_name='role',
        external_id='myexternalid',
        role_duration='43200',
        role_arn=None,
        session_name='mysessionname',
        mfa_token='123123',
        force_refresh=True,
        auto_refresh=False,
        region=None,
        output_profile=None,
    )
    profiles = {
        'role': {
            'role_arn': 'myrolearn',
            'source_profile': 'user',
        },
        'user': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'mfa_serial': 'mymfaserial',
        },
    }

    result = default_plugins.get_credentials(config, arguments, profiles)
    aws_lib.get_session_token.assert_not_called()
    aws_lib.assume_role.assert_called_with(
        { 'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': None, 'Region': None },
        'myrolearn',
        'mysessionname',
        region=None,
        external_id='myexternalid',
        role_duration=43200,
        mfa_serial='mymfaserial',
        mfa_token='123123',
        tags=None,
    )
    assert result == aws_lib.assume_role.return_value


@patch.object(autoawsume, 'create_autoawsume_profile')
@patch.object(default_plugins, 'aws_lib')
def test_get_credentials_role_duration_auto_refresh_exit(aws_lib: MagicMock, create_autoawsume_profile: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        target_profile_name='role',
        external_id='myexternalid',
        role_duration='43200',
        role_arn=None,
        session_name='mysessionname',
        mfa_token='123123',
        force_refresh=True,
        auto_refresh=True,
        region=None,
        output_profile=None,
    )
    profiles = {
        'role': {
            'role_arn': 'myrolearn',
            'source_profile': 'user',
        },
        'user': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'mfa_serial': 'mymfaserial',
        },
    }
    with pytest.raises(exceptions.ValidationException):
        default_plugins.get_credentials(config, arguments, profiles)


@patch.object(autoawsume, 'create_autoawsume_profile')
@patch.object(default_plugins, 'aws_lib')
def test_get_credentials_user(aws_lib: MagicMock, create_autoawsume_profile: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        target_profile_name='user',
        external_id=None,
        role_duration=None,
        role_arn=None,
        session_name=None,
        mfa_token='123123',
        force_refresh=True,
        auto_refresh=False,
        region=None,
        output_profile=None,
    )
    profiles = {
        'role': {
            'role_arn': 'myrolearn',
            'source_profile': 'user',
        },
        'user': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
            'mfa_serial': 'mymfaserial',
        },
    }

    result = default_plugins.get_credentials(config, arguments, profiles)
    aws_lib.get_session_token.assert_called_with(
        { 'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': None, 'Region': None },
        region=None,
        mfa_serial='mymfaserial',
        mfa_token='123123',
        ignore_cache=True,
        duration_seconds=None,
    )
    assert result == aws_lib.get_session_token.return_value


@patch.object(autoawsume, 'create_autoawsume_profile')
@patch.object(default_plugins, 'aws_lib')
def test_get_credentials_no_mfa_role(aws_lib: MagicMock, create_autoawsume_profile: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        target_profile_name='role',
        external_id='myexternalid',
        role_duration=None,
        role_arn=None,
        session_name='mysessionname',
        mfa_token='123123',
        force_refresh=True,
        auto_refresh=False,
        region=None,
        output_profile=None,
    )
    profiles = {
        'role': {
            'role_arn': 'myrolearn',
            'source_profile': 'user',
        },
        'user': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }

    result = default_plugins.get_credentials(config, arguments, profiles)
    aws_lib.get_session_token.assert_not_called()
    aws_lib.assume_role.assert_called_with(
        { 'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': None, 'Region': None },
        'myrolearn',
        'mysessionname',
        region=None,
        external_id='myexternalid',
        role_duration=0,
        tags=None,
    )
    assert result == aws_lib.assume_role.return_value


@patch.object(autoawsume, 'create_autoawsume_profile')
@patch.object(default_plugins, 'aws_lib')
def test_get_credentials_no_mfa_user(aws_lib: MagicMock, create_autoawsume_profile: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        target_profile_name='user',
        external_id='myexternalid',
        role_duration=None,
        role_arn=None,
        session_name='mysessionname',
        mfa_token='123123',
        force_refresh=True,
        auto_refresh=False,
        region=None,
        output_profile=None,
    )
    profiles = {
        'role': {
            'role_arn': 'myrolearn',
            'source_profile': 'user',
        },
        'user': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }

    result = default_plugins.get_credentials(config, arguments, profiles)
    aws_lib.get_session_token.assert_not_called()
    aws_lib.assume_role.assert_not_called()
    assert result == {
        'AccessKeyId': 'AKIA...',
        'SecretAccessKey': 'SECRET',
        'SessionToken': None,
        'Region': None,
    }


@patch.object(default_plugins, 'assume_role_from_cli')
@patch.object(autoawsume, 'create_autoawsume_profile')
@patch.object(default_plugins, 'aws_lib')
def test_get_credentials_role_from_cli(aws_lib: MagicMock, create_autoawsume_profile: MagicMock, assume_role_from_cli: MagicMock):
    config = {}
    arguments = argparse.Namespace(
        target_profile_name='user',
        external_id='myexternalid',
        role_duration=None,
        role_arn='myrolearn',
        source_profile=None,
        session_name='mysessionname',
        mfa_token='123123',
        force_refresh=True,
        auto_refresh=False,
        region=None,
        output_profile=None,
    )
    profiles = {
        'role': {
            'role_arn': 'myrolearn',
            'source_profile': 'user',
        },
        'user': {
            'aws_access_key_id': 'AKIA...',
            'aws_secret_access_key': 'SECRET',
        },
    }

    result = default_plugins.get_credentials(config, arguments, profiles)
    assert result == assume_role_from_cli.return_value


@patch.object(default_plugins, 'aws_lib')
def test_post_add_arguments_session_tags(aws_lib: MagicMock):
    config = {}
    arguments = generate_namespace_with_defaults(
        role_duration='43200',
        session_name=None,
        role_arn='arn:aws:iam::123123123123:role/myrole',
        external_id=None,
        mfa_token=None,
        force_refresh=False,
        session_tags='foo=bar,biz=baz'
    )
    parser = argparse.ArgumentParser()
    default_plugins.post_add_arguments(config, arguments, parser)
    default_plugins.get_credentials(config, arguments, {})
    aws_lib.assume_role.assert_called_with(
        config,
        arguments.role_arn,
        'awsume-cli-role',
        external_id=arguments.external_id,
        role_duration='43200',
        tags=[
            {
                'Key': 'foo',
                'Value': 'bar',
            }, {
                'Key': 'biz',
                'Value': 'baz',
            }
        ],
        region=arguments.region,
    )
