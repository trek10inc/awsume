import sys
import argparse
import colorama
import datetime
import pluggy
import pytest
from io import StringIO
from awsume.awsumepy import app
from awsume.awsumepy.lib.config_management import load_config
from awsume.awsumepy.lib import exceptions
from unittest.mock import patch, MagicMock, mock_open
from awsume.awsumepy import hookspec
from awsume.awsumepy.lib import aws


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
    parser.parse_args.return_value = argparse.Namespace(refresh_autocomplete=False, list_plugins=False)
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
    parser.parse_args.return_value = argparse.Namespace(refresh_autocomplete=True, list_plugins=False)
    ArgumentParser.return_value = parser
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    obj.plugin_manager.hook.get_profile_names.return_value = [['profile1', 'profile2', 'profile3'], ['pluginProfile']]

    with pytest.raises(exceptions.EarlyExit):
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


@patch.object(app, 'get_role_chain')
@patch.object(sys.stdin, 'isatty')
@patch.object(app.Awsume, '__init__')
def test_get_credentials(__init__: MagicMock, isatty: MagicMock, get_role_chain: MagicMock):
    __init__.return_value = None
    args = argparse.Namespace(json=None, with_saml=False, with_web_identity=False, auto_refresh=False, target_profile_name='profilename')
    profiles = {}
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    isatty.return_value = True
    obj.plugin_manager.hook.get_credentials.return_value = [{'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': 'LONGSECRET', 'Region': 'us-east-1'}]
    get_role_chain.return_value = ['profilename']

    result = obj.get_credentials(args, profiles)

    obj.plugin_manager.hook.get_credentials.assert_called_with(config=obj.config, arguments=args, profiles=profiles)
    assert result == {'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': 'LONGSECRET', 'Region': 'us-east-1'}


@patch.object(aws, 'assume_role_with_saml')
@patch.object(app, 'get_role_chain')
@patch.object(sys.stdin, 'isatty')
@patch.object(app.Awsume, '__init__')
def test_get_saml_credentials(__init__: MagicMock, isatty: MagicMock, get_role_chain: MagicMock, assume_role_with_saml: MagicMock):
    __init__.return_value = None
    args = argparse.Namespace(
        json=None,
        with_saml=False,
        with_web_identity=False,
        auto_refresh=False,
        target_profile_name='profilename',
        role_duration=3600,
        principal_arn='arn:aws:iam::FAKE:saml-provider/MySamlProvider',
        role_arn='arn:aws:iam::FAKE:role/FAKE'
    )
    profiles = {}
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    isatty.return_value = True
    assertion = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPHNhbWwycDpSZXNwb25zZSBEZXN0aW5hdGlvbj0iaHR0cHM6Ly9zaWduaW4uYXdzLmFtYXpvbi5jb20vc2FtbCIgSUQ9IkZBS0UiIElzc3VlSW5zdGFudD0iMjAyMy0wOC0wN1QyMTozNzowMi45MjdaIiBWZXJzaW9uPSIyLjAiIHhtbG5zOnNhbWwycD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOnByb3RvY29sIiB4bWxuczp4cz0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEiPjxzYW1sMjpJc3N1ZXIgRm9ybWF0PSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6bmFtZWlkLWZvcm1hdDplbnRpdHkiIHhtbG5zOnNhbWwyPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YXNzZXJ0aW9uIj5odHRwOi8vd3d3Lm9rdGEuY29tL0ZBS0U8L3NhbWwyOklzc3Vlcj48ZHM6U2lnbmF0dXJlIHhtbG5zOmRzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjIj48ZHM6U2lnbmVkSW5mbz48ZHM6Q2Fub25pY2FsaXphdGlvbk1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyI+PC9kczpDYW5vbmljYWxpemF0aW9uTWV0aG9kPjxkczpTaWduYXR1cmVNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNyc2Etc2hhMjU2Ij48L2RzOlNpZ25hdHVyZU1ldGhvZD48ZHM6UmVmZXJlbmNlIFVSST0iI0ZBS0UiPjxkczpUcmFuc2Zvcm1zPjxkczpUcmFuc2Zvcm0gQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjZW52ZWxvcGVkLXNpZ25hdHVyZSI+PC9kczpUcmFuc2Zvcm0+PGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyI+PGVjOkluY2x1c2l2ZU5hbWVzcGFjZXMgUHJlZml4TGlzdD0ieHMiIHhtbG5zOmVjPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiPjwvZWM6SW5jbHVzaXZlTmFtZXNwYWNlcz48L2RzOlRyYW5zZm9ybT48L2RzOlRyYW5zZm9ybXM+PGRzOkRpZ2VzdE1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMDQveG1sZW5jI3NoYTI1NiI+PC9kczpEaWdlc3RNZXRob2Q+PGRzOkRpZ2VzdFZhbHVlPkZBS0U8L2RzOkRpZ2VzdFZhbHVlPjwvZHM6UmVmZXJlbmNlPjwvZHM6U2lnbmVkSW5mbz48ZHM6U2lnbmF0dXJlVmFsdWU+RkFLRTwvZHM6U2lnbmF0dXJlVmFsdWU+PGRzOktleUluZm8+PGRzOlg1MDlEYXRhPjxkczpYNTA5Q2VydGlmaWNhdGU+RkFLRTwvZHM6WDUwOUNlcnRpZmljYXRlPjwvZHM6WDUwOURhdGE+PC9kczpLZXlJbmZvPjwvZHM6U2lnbmF0dXJlPjxzYW1sMnA6U3RhdHVzIHhtbG5zOnNhbWwycD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOnByb3RvY29sIj48c2FtbDJwOlN0YXR1c0NvZGUgVmFsdWU9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpzdGF0dXM6U3VjY2VzcyI+PC9zYW1sMnA6U3RhdHVzQ29kZT48L3NhbWwycDpTdGF0dXM+PHNhbWwyOkFzc2VydGlvbiBJRD0iRkFLRSIgSXNzdWVJbnN0YW50PSIyMDIzLTA4LTA3VDIxOjM3OjAyLjkyN1oiIFZlcnNpb249IjIuMCIgeG1sbnM6c2FtbDI9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iIHhtbG5zOnhzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYSI+PHNhbWwyOklzc3VlciBGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpuYW1laWQtZm9ybWF0OmVudGl0eSIgeG1sbnM6c2FtbDI9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iPmh0dHA6Ly93d3cub2t0YS5jb20vRkFLRTwvc2FtbDI6SXNzdWVyPjxkczpTaWduYXR1cmUgeG1sbnM6ZHM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyMiPjxkczpTaWduZWRJbmZvPjxkczpDYW5vbmljYWxpemF0aW9uTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8xMC94bWwtZXhjLWMxNG4jIj48L2RzOkNhbm9uaWNhbGl6YXRpb25NZXRob2Q+PGRzOlNpZ25hdHVyZU1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMDQveG1sZHNpZy1tb3JlI3JzYS1zaGEyNTYiPjwvZHM6U2lnbmF0dXJlTWV0aG9kPjxkczpSZWZlcmVuY2UgVVJJPSIjRkFLRSI+PGRzOlRyYW5zZm9ybXM+PGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNlbnZlbG9wZWQtc2lnbmF0dXJlIj48L2RzOlRyYW5zZm9ybT48ZHM6VHJhbnNmb3JtIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8xMC94bWwtZXhjLWMxNG4jIj48ZWM6SW5jbHVzaXZlTmFtZXNwYWNlcyBQcmVmaXhMaXN0PSJ4cyIgeG1sbnM6ZWM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyI+PC9lYzpJbmNsdXNpdmVOYW1lc3BhY2VzPjwvZHM6VHJhbnNmb3JtPjwvZHM6VHJhbnNmb3Jtcz48ZHM6RGlnZXN0TWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8wNC94bWxlbmMjc2hhMjU2Ij48L2RzOkRpZ2VzdE1ldGhvZD48ZHM6RGlnZXN0VmFsdWU+RkFLRTwvZHM6RGlnZXN0VmFsdWU+PC9kczpSZWZlcmVuY2U+PC9kczpTaWduZWRJbmZvPjxkczpTaWduYXR1cmVWYWx1ZT5GQUtFPC9kczpTaWduYXR1cmVWYWx1ZT48ZHM6S2V5SW5mbz48ZHM6WDUwOURhdGE+PGRzOlg1MDlDZXJ0aWZpY2F0ZT5GQUtFPC9kczpYNTA5Q2VydGlmaWNhdGU+PC9kczpYNTA5RGF0YT48L2RzOktleUluZm8+PC9kczpTaWduYXR1cmU+PHNhbWwyOlN1YmplY3QgeG1sbnM6c2FtbDI9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iPjxzYW1sMjpOYW1lSUQgRm9ybWF0PSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6bmFtZWlkLWZvcm1hdDp1bnNwZWNpZmllZCI+RkFLRTwvc2FtbDI6TmFtZUlEPjxzYW1sMjpTdWJqZWN0Q29uZmlybWF0aW9uIE1ldGhvZD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmNtOmJlYXJlciI+PHNhbWwyOlN1YmplY3RDb25maXJtYXRpb25EYXRhIE5vdE9uT3JBZnRlcj0iMjAyMy0wOC0wN1QyMTo0MjowMi45MjdaIiBSZWNpcGllbnQ9Imh0dHBzOi8vc2lnbmluLmF3cy5hbWF6b24uY29tL3NhbWwiPjwvc2FtbDI6U3ViamVjdENvbmZpcm1hdGlvbkRhdGE+PC9zYW1sMjpTdWJqZWN0Q29uZmlybWF0aW9uPjwvc2FtbDI6U3ViamVjdD48c2FtbDI6Q29uZGl0aW9ucyBOb3RCZWZvcmU9IjIwMjMtMDgtMDdUMjE6MzI6MDIuOTI3WiIgTm90T25PckFmdGVyPSIyMDIzLTA4LTA3VDIxOjQyOjAyLjkyN1oiIHhtbG5zOnNhbWwyPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YXNzZXJ0aW9uIj48c2FtbDI6QXVkaWVuY2VSZXN0cmljdGlvbj48c2FtbDI6QXVkaWVuY2U+dXJuOmFtYXpvbjp3ZWJzZXJ2aWNlczwvc2FtbDI6QXVkaWVuY2U+PC9zYW1sMjpBdWRpZW5jZVJlc3RyaWN0aW9uPjwvc2FtbDI6Q29uZGl0aW9ucz48c2FtbDI6QXV0aG5TdGF0ZW1lbnQgQXV0aG5JbnN0YW50PSIyMDIzLTA4LTA3VDIxOjM3OjAyLjkyN1oiIFNlc3Npb25JbmRleD0iRkFLRSIgeG1sbnM6c2FtbDI9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iPjxzYW1sMjpBdXRobkNvbnRleHQ+PHNhbWwyOkF1dGhuQ29udGV4dENsYXNzUmVmPnVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphYzpjbGFzc2VzOlBhc3N3b3JkUHJvdGVjdGVkVHJhbnNwb3J0PC9zYW1sMjpBdXRobkNvbnRleHRDbGFzc1JlZj48L3NhbWwyOkF1dGhuQ29udGV4dD48L3NhbWwyOkF1dGhuU3RhdGVtZW50PjxzYW1sMjpBdHRyaWJ1dGVTdGF0ZW1lbnQgeG1sbnM6c2FtbDI9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0iaHR0cHM6Ly9hd3MuYW1hem9uLmNvbS9TQU1ML0F0dHJpYnV0ZXMvUm9sZSIgTmFtZUZvcm1hdD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmF0dHJuYW1lLWZvcm1hdDp1cmkiPjxzYW1sMjpBdHRyaWJ1dGVWYWx1ZSB4bWxuczp4cz0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEiIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhzaTp0eXBlPSJ4czpzdHJpbmciPmFybjphd3M6aWFtOjpGQUtFOnNhbWwtcHJvdmlkZXIvTXlTYW1sUHJvdmlkZXIsYXJuOmF3czppYW06OkZBS0U6cm9sZS9GQUtFPC9zYW1sMjpBdHRyaWJ1dGVWYWx1ZT48L3NhbWwyOkF0dHJpYnV0ZT48c2FtbDI6QXR0cmlidXRlIE5hbWU9Imh0dHBzOi8vYXdzLmFtYXpvbi5jb20vU0FNTC9BdHRyaWJ1dGVzL1JvbGVTZXNzaW9uTmFtZSIgTmFtZUZvcm1hdD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmF0dHJuYW1lLWZvcm1hdDpiYXNpYyI+PHNhbWwyOkF0dHJpYnV0ZVZhbHVlIHhtbG5zOnhzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYSIgeG1sbnM6eHNpPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYS1pbnN0YW5jZSIgeHNpOnR5cGU9InhzOnN0cmluZyI+RkFLRTwvc2FtbDI6QXR0cmlidXRlVmFsdWU+PC9zYW1sMjpBdHRyaWJ1dGU+PHNhbWwyOkF0dHJpYnV0ZSBOYW1lPSJodHRwczovL2F3cy5hbWF6b24uY29tL1NBTUwvQXR0cmlidXRlcy9TZXNzaW9uRHVyYXRpb24iIE5hbWVGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphdHRybmFtZS1mb3JtYXQ6YmFzaWMiPjxzYW1sMjpBdHRyaWJ1dGVWYWx1ZSB4bWxuczp4cz0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEiIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhzaTp0eXBlPSJ4czpzdHJpbmciPjM2MDA8L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjwvc2FtbDI6QXR0cmlidXRlU3RhdGVtZW50Pjwvc2FtbDI6QXNzZXJ0aW9uPjwvc2FtbDJwOlJlc3BvbnNlPg=="
    obj.plugin_manager.hook.get_credentials_with_saml.return_value = [assertion]
    get_role_chain.return_value = ['profilename']

    result = obj.get_saml_credentials(args, profiles)

    assume_role_with_saml.assert_called_with(
        'arn:aws:iam::FAKE:role/FAKE',
        'arn:aws:iam::FAKE:saml-provider/MySamlProvider',
        assertion,
        role_duration=3600,
        region=None,
    )


@patch.object(app, 'get_role_chain')
@patch.object(sys.stdin, 'isatty')
@patch.object(app, 'safe_print')
@patch.object(app.Awsume, '__init__')
def test_get_credentials_profile_not_found_error(__init__: MagicMock, safe_print: MagicMock, isatty: MagicMock, get_role_chain: MagicMock):
    __init__.return_value = None
    args = argparse.Namespace(json=None, with_saml=False, with_web_identity=False, auto_refresh=False, target_profile_name='profilename')
    profiles = {}
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    isatty.return_value = True
    get_role_chain.return_value = ['profilename']

    obj.plugin_manager.hook.get_credentials.side_effect = exceptions.ProfileNotFoundError()
    with pytest.raises(exceptions.ProfileNotFoundError):
        obj.get_credentials(args, profiles)
    obj.plugin_manager.hook.catch_profile_not_found_exception.assert_called_with(config=obj.config, arguments=args, error=obj.plugin_manager.hook.get_credentials.side_effect, profiles=profiles)


@patch.object(app, 'get_role_chain')
@patch.object(sys.stdin, 'isatty')
@patch.object(app, 'safe_print')
@patch.object(app.Awsume, '__init__')
def test_get_credentials_invalid_profile_error(__init__: MagicMock, safe_print: MagicMock, isatty: MagicMock, get_role_chain: MagicMock):
    __init__.return_value = None
    args = argparse.Namespace(json=None, with_saml=False, with_web_identity=False, auto_refresh=False, target_profile_name='profilename')
    profiles = {}
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    isatty.return_value = True
    get_role_chain.return_value = ['profilename']

    obj.plugin_manager.hook.get_credentials.side_effect = exceptions.InvalidProfileError(profile_name='profile')
    with pytest.raises(exceptions.InvalidProfileError):
        obj.get_credentials(args, profiles)
    obj.plugin_manager.hook.catch_invalid_profile_exception.assert_called_with(config=obj.config, arguments=args, error=obj.plugin_manager.hook.get_credentials.side_effect, profiles=profiles)


@patch.object(app, 'get_role_chain')
@patch.object(sys.stdin, 'isatty')
@patch.object(app, 'safe_print')
@patch.object(app.Awsume, '__init__')
def test_get_credentials_user_authentication_error(__init__: MagicMock, safe_print: MagicMock, isatty: MagicMock, get_role_chain: MagicMock):
    __init__.return_value = None
    args = argparse.Namespace(json=None, with_saml=False, with_web_identity=False, auto_refresh=False, target_profile_name='profilename')
    profiles = {}
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    isatty.return_value = True
    get_role_chain.return_value = ['profilename']

    obj.plugin_manager.hook.get_credentials.side_effect = exceptions.UserAuthenticationError()
    with pytest.raises(exceptions.UserAuthenticationError):
        obj.get_credentials(args, profiles)
    obj.plugin_manager.hook.catch_user_authentication_error.assert_called_with(config=obj.config, arguments=args, error=obj.plugin_manager.hook.get_credentials.side_effect, profiles=profiles)


@patch.object(app, 'get_role_chain')
@patch.object(sys.stdin, 'isatty')
@patch.object(app, 'safe_print')
@patch.object(app.Awsume, '__init__')
def test_get_credentials_role_authentication_error(__init__: MagicMock, safe_print: MagicMock, isatty: MagicMock, get_role_chain: MagicMock):
    __init__.return_value = None
    args = argparse.Namespace(json=None, with_saml=False, with_web_identity=False, auto_refresh=False, target_profile_name='profilename')
    profiles = {}
    obj = app.Awsume()
    obj.config = {}
    obj.plugin_manager = MagicMock()
    isatty.return_value = True
    get_role_chain.return_value = ['profilename']

    obj.plugin_manager.hook.get_credentials.side_effect = exceptions.RoleAuthenticationError()
    with pytest.raises(exceptions.RoleAuthenticationError):
        obj.get_credentials(args, profiles)
    obj.plugin_manager.hook.catch_role_authentication_error.assert_called_with(config=obj.config, arguments=args, error=obj.plugin_manager.hook.get_credentials.side_effect, profiles=profiles)


@patch.object(app, 'is_mutable_profile')
@patch('sys.stdout', new_callable=StringIO)
@patch.object(app.Awsume, '__init__')
def test_export_data(__init__: MagicMock, stdout: MagicMock, is_mutable_profile: MagicMock):
    __init__.return_value = None
    obj = app.Awsume()
    awsume_list = ['data1', 'data2', 'data3']
    awsume_flag = 'flag'
    obj.is_interactive = True
    is_mutable_profile.return_value = True
    arguments = argparse.Namespace(output_profile=None, auto_refresh=False)
    profiles = {}
    credentials = {}

    obj.export_data(arguments, profiles, credentials, awsume_flag, awsume_list)

    assert stdout.getvalue() == 'flag data1 data2 data3\n'


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
    obj.get_credentials.return_value = {'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': 'LONGSECRET', 'Region': 'us-east-1', 'Expiration': datetime.datetime.now()}
    isatty.return_value = True

    obj.run([])

    obj.export_data.assert_called_with(obj.parse_args.return_value, obj.get_profiles.return_value, obj.get_credentials.return_value, 'Awsume', [
        'AKIA...', 'SECRET', 'LONGSECRET', 'us-east-1', 'default', 'None', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
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
    obj.parse_args.return_value = argparse.Namespace(with_saml=False, with_web_identity=False, auto_refresh=True, target_profile_name='default', json=None, output_profile=None)
    obj.get_credentials.return_value = {'AccessKeyId': 'AKIA...', 'SecretAccessKey': 'SECRET', 'SessionToken': 'LONGSECRET', 'Region': 'us-east-1', 'Expiration': datetime.datetime.now()}
    isatty.return_value = True

    obj.run([])

    obj.export_data.assert_called_with(obj.parse_args.return_value, obj.get_profiles.return_value, obj.get_credentials.return_value, 'Auto', [
        'autoawsume-default', 'us-east-1', 'default',
    ])
