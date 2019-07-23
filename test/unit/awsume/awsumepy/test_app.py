import sys
import argparse
import colorama
import pluggy
import pytest
from io import StringIO
from awsume.awsumepy import app
from awsume.awsumepy.lib.config_management import load_config
from awsume.awsumepy.lib.exceptions import ProfileNotFoundError, InvalidProfileError, UserAuthenticationError, RoleAuthenticationError
from unittest.mock import patch, MagicMock, mock_open
from awsume.awsumepy import hookspec


@patch.object(app, 'load_config')
@patch.object(app.Awsume, 'get_plugin_manager')
@patch.object(colorama, 'init')
def test_app_init(init: MagicMock, get_plugin_manager: MagicMock, load_config: MagicMock):
    obj = app.Awsume()

    init.assert_called_with(autoreset=True)

    get_plugin_manager.assert_called()
    load_config.assert_called()
    assert obj.config == load_config.return_value
    assert obj.plugin_manager == get_plugin_manager.return_value


@patch('pluggy.PluginManager')
@patch.object(app.Awsume, '__init__')
def test_get_plugin_manager(__init__: MagicMock, PluginManager: MagicMock):
    __init__.return_value = None
    pm = MagicMock()
    PluginManager.return_value = pm

    obj = app.Awsume()
    response = obj.get_plugin_manager()

    PluginManager.assert_called_with('awsume')
    pm.add_hookspecs.assert_called_once_with(hookspec)
    pm.register.assert_called_once()
    pm.load_setuptools_entrypoints.assert_called_once_with('awsume')
    assert response == pm


@patch('argparse.ArgumentParser')
@patch.object(app.Awsume, '__init__')
def test_parse_args(__init__: MagicMock, ArgumentParser: MagicMock):
    __init__.return_value = None
    parser = MagicMock()
    parser.parse_args.return_value = argparse.Namespace(refresh_autocomplete=False)
    ArgumentParser.return_value = parser
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()

    result = obj.parse_args([])

    obj.plugin_manager.hook.pre_add_arguments.assert_called()
    obj.plugin_manager.hook.add_arguments.assert_called()
    obj.plugin_manager.hook.post_add_arguments.assert_called()
    assert result == parser.parse_args.return_value


@patch('json.dump')
@patch.object(app, 'open')
@patch('argparse.ArgumentParser')
@patch.object(app.Awsume, '__init__')
def test_parse_args_refresh_autocomplete(__init__: MagicMock, ArgumentParser: MagicMock, open: MagicMock, json_dump: MagicMock):
    __init__.return_value = None
    parser = MagicMock()
    parser.parse_args.return_value = argparse.Namespace(refresh_autocomplete=True)
    ArgumentParser.return_value = parser
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    obj.plugin_manager.hook.get_profile_names.return_value = [['profile1', 'profile2', 'profile3'], ['pluginProfile']]

    with pytest.raises(SystemExit):
        obj.parse_args([])

    json_dump.assert_called_with({'profile-names': ['profile1', 'profile2', 'profile3', 'pluginProfile']}, open.return_value)
    open.assert_called()
    obj.plugin_manager.hook.get_profile_names.assert_called_with(config=obj.config, arguments=parser.parse_args.return_value)


@patch.object(app, 'aggregate_profiles')
@patch.object(app, 'get_aws_files')
@patch.object(app.Awsume, '__init__')
def test_get_profiles(__init__: MagicMock, get_aws_files: MagicMock, aggregate_profiles: MagicMock):
    __init__.return_value = None
    get_aws_files.return_value = 'config', 'credentials'
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()

    result = obj.get_profiles(argparse.Namespace())

    obj.plugin_manager.hook.pre_collect_aws_profiles.assert_called_with(config=obj.config, config_file='config', credentials_file='credentials', arguments=argparse.Namespace())
    obj.plugin_manager.hook.collect_aws_profiles.assert_called_with(config=obj.config, config_file='config', credentials_file='credentials', arguments=argparse.Namespace())
    obj.plugin_manager.hook.post_collect_aws_profiles.assert_called_with(config=obj.config, arguments=argparse.Namespace(), profiles=aggregate_profiles.return_value)
    aggregate_profiles.assert_called_with(obj.plugin_manager.hook.collect_aws_profiles.return_value)

    assert result == aggregate_profiles.return_value


@patch.object(sys.stdin, 'isatty')
@patch.object(app.Awsume, '__init__')
def test_get_credentials(__init__: MagicMock, isatty: MagicMock):
    __init__.return_value = None
    args = argparse.Namespace(json=None, with_saml=False, with_web_identity=False)
    profiles = {}
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    isatty.return_value = True
    obj.plugin_manager.hook.get_credentials.return_value = [{'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': 'LONGSECRET', 'Region': 'us-east-1'}]

    result = obj.get_credentials(args, profiles)

    obj.plugin_manager.hook.get_credentials.assert_called_with(config=obj.config, arguments=args, profiles=profiles)
    assert result == {'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': 'LONGSECRET', 'Region': 'us-east-1'}


@patch.object(sys.stdin, 'isatty')
@patch.object(app, 'safe_print')
@patch.object(app.Awsume, '__init__')
def test_get_credentials_profile_not_found_error(__init__: MagicMock, safe_print: MagicMock, isatty: MagicMock):
    __init__.return_value = None
    args = argparse.Namespace(json=None, with_saml=False, with_web_identity=False)
    profiles = {}
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    isatty.return_value = True

    obj.plugin_manager.hook.get_credentials.side_effect = ProfileNotFoundError()
    with pytest.raises(SystemExit):
        obj.get_credentials(args, profiles)
    obj.plugin_manager.hook.catch_profile_not_found_exception.assert_called_with(config=obj.config, arguments=args, error=obj.plugin_manager.hook.get_credentials.side_effect, profiles=profiles)


@patch.object(sys.stdin, 'isatty')
@patch.object(app, 'safe_print')
@patch.object(app.Awsume, '__init__')
def test_get_credentials_invalid_profile_error(__init__: MagicMock, safe_print: MagicMock, isatty: MagicMock):
    __init__.return_value = None
    args = argparse.Namespace(json=None, with_saml=False, with_web_identity=False)
    profiles = {}
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    isatty.return_value = True

    obj.plugin_manager.hook.get_credentials.side_effect = InvalidProfileError(profile_name='profile')
    with pytest.raises(SystemExit):
        obj.get_credentials(args, profiles)
    obj.plugin_manager.hook.catch_invalid_profile_exception.assert_called_with(config=obj.config, arguments=args, error=obj.plugin_manager.hook.get_credentials.side_effect, profiles=profiles)


@patch.object(sys.stdin, 'isatty')
@patch.object(app, 'safe_print')
@patch.object(app.Awsume, '__init__')
def test_get_credentials_user_authentication_error(__init__: MagicMock, safe_print: MagicMock, isatty: MagicMock):
    __init__.return_value = None
    args = argparse.Namespace(json=None, with_saml=False, with_web_identity=False)
    profiles = {}
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    isatty.return_value = True

    obj.plugin_manager.hook.get_credentials.side_effect = UserAuthenticationError()
    with pytest.raises(SystemExit):
        obj.get_credentials(args, profiles)
    obj.plugin_manager.hook.catch_user_authentication_error.assert_called_with(config=obj.config, arguments=args, error=obj.plugin_manager.hook.get_credentials.side_effect, profiles=profiles)


@patch.object(sys.stdin, 'isatty')
@patch.object(app, 'safe_print')
@patch.object(app.Awsume, '__init__')
def test_get_credentials_role_authentication_error(__init__: MagicMock, safe_print: MagicMock, isatty: MagicMock):
    __init__.return_value = None
    args = argparse.Namespace(json=None, with_saml=False, with_web_identity=False)
    profiles = {}
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    isatty.return_value = True

    obj.plugin_manager.hook.get_credentials.side_effect = RoleAuthenticationError()
    with pytest.raises(SystemExit):
        obj.get_credentials(args, profiles)
    obj.plugin_manager.hook.catch_role_authentication_error.assert_called_with(config=obj.config, arguments=args, error=obj.plugin_manager.hook.get_credentials.side_effect, profiles=profiles)


@patch('sys.stdout', new_callable=StringIO)
@patch.object(app.Awsume, '__init__')
def test_export_data(__init__: MagicMock, stdout: MagicMock):
    __init__.return_value = None
    obj = app.Awsume()
    awsume_list = ['data1', 'data2', 'data3']
    awsume_flag = 'flag'
    obj.export_data(awsume_flag, awsume_list)

    assert stdout.getvalue() == 'flag\ndata1 data2 data3\n'


@patch.object(sys.stdin, 'isatty')
@patch.object(app.Awsume, '__init__')
def test_run(__init__: MagicMock, isatty: MagicMock):
    __init__.return_value = None
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    obj.parse_args = MagicMock()
    obj.get_profiles = MagicMock()
    obj.export_data = MagicMock()
    obj.get_credentials = MagicMock()
    obj.parse_args.return_value = argparse.Namespace(with_saml=False, with_web_identity=False, auto_refresh=False, target_profile_name='default', json=None)
    obj.get_credentials.return_value = {'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': 'LONGSECRET', 'Region': 'us-east-1'}
    isatty.return_value = True

    obj.run([])

    obj.export_data.assert_called_with('Awsume', [
        'AKIA...', 'SECRET', 'LONGSECRET', 'us-east-1', 'default'
    ])


@patch.object(sys.stdin, 'isatty')
@patch.object(app.Awsume, '__init__')
def test_run_auto_refresh(__init__: MagicMock, isatty: MagicMock):
    __init__.return_value = None
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    obj.parse_args = MagicMock()
    obj.get_profiles = MagicMock()
    obj.export_data = MagicMock()
    obj.get_credentials = MagicMock()
    obj.parse_args.return_value = argparse.Namespace(with_saml=False, with_web_identity=False, auto_refresh=True, target_profile_name='default', json=None)
    obj.get_credentials.return_value = {'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': 'LONGSECRET', 'Region': 'us-east-1'}
    isatty.return_value = True

    obj.run([])

    obj.export_data.assert_called_with('Auto', [
        'autoawsume-default', 'us-east-1', 'default'
    ])


# TODO: This belongs in the test_get_credentials section
# @patch.object(sys.stdin, 'isatty')
# @patch.object(app.Awsume, '__init__')
# def test_run_with_saml(__init__: MagicMock, isatty: MagicMock):
#     __init__.return_value = None
#     obj = app.Awsume()
#     obj.config = {}
#     obj.plugin_manager = MagicMock()
#     obj.parse_args = MagicMock()
#     obj.get_profiles = MagicMock()
#     obj.export_data = MagicMock()
#     obj.get_credentials = MagicMock()
#     obj.parse_args.return_value = argparse.Namespace(with_saml=True, with_web_identity=False, auto_refresh=False, target_profile_name='default', json=None)
#     obj.plugin_manager.hook.get_credentials_with_saml.return_value = [{'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': 'LONGSECRET', 'Region': 'us-east-1'}]
#     isatty.return_value = True

#     obj.run([])

#     obj.export_data.assert_called_with('Awsume', [
#         'AKIA...', 'SECRET', 'LONGSECRET', 'us-east-1', 'default'
#     ])


# @patch.object(sys.stdin, 'isatty')
# @patch.object(app.Awsume, '__init__')
# def test_run_with_web_identity(__init__: MagicMock, isatty: MagicMock):
#     __init__.return_value = None
#     obj = app.Awsume()
#     obj.config = {}
#     obj.plugin_manager = MagicMock()
#     obj.parse_args = MagicMock()
#     obj.get_profiles = MagicMock()
#     obj.export_data = MagicMock()
#     obj.get_credentials = MagicMock()
#     obj.parse_args.return_value = argparse.Namespace(with_saml=False, with_web_identity=True, auto_refresh=False, target_profile_name='default', json=None)
#     obj.plugin_manager.hook.get_credentials_with_web_identity.return_value = [{'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': 'LONGSECRET', 'Region': 'us-east-1'}]
#     isatty.return_value = True

#     obj.run([])

#     obj.export_data.assert_called_with('Awsume', [
#         'AKIA...', 'SECRET', 'LONGSECRET', 'us-east-1', 'default'
#     ])



# @patch.object(sys.stdin, 'isatty')
# @patch.object(app, 'safe_print')
# @patch.object(app.Awsume, '__init__')
# def test_run_no_credentials(__init__: MagicMock, safe_print: MagicMock, isatty: MagicMock):
#     __init__.return_value = None
#     obj = app.Awsume()
#     obj.config = {}
#     obj.plugin_manager = MagicMock()
#     obj.parse_args = MagicMock()
#     obj.get_profiles = MagicMock()
#     obj.export_data = MagicMock()
#     obj.get_credentials = MagicMock()
#     obj.parse_args.return_value = argparse.Namespace(with_saml=False, with_web_identity=False, auto_refresh=False, target_profile_name='default', json=None)
#     obj.get_credentials.return_value = []
#     isatty.return_value = True

#     with pytest.raises(SystemExit):
#         obj.run([])
