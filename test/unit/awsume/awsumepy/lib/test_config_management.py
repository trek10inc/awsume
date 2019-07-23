import os
import json
import pytest
from unittest.mock import patch, MagicMock

import yaml
from awsume.awsumepy.lib import config_management


@patch('yaml.safe_load')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_load_config(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock, yaml_load: MagicMock):
    exists.return_value = True
    isfile.return_value = True
    yaml_load.return_value = {'key': 'value'}

    result = config_management.load_config()

    assert result == yaml_load.return_value
    makedirs.assert_not_called()


@patch('yaml.safe_load')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_load_config_no_path(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock, yaml_load: MagicMock):
    exists.return_value = False
    isfile.return_value = True
    yaml_load.return_value = {'key': 'value'}

    result = config_management.load_config()

    assert result == yaml_load.return_value
    makedirs.assert_called()
    open.assert_called_once()
    makedirs.assert_called_once()


@patch('yaml.safe_load')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_load_config_no_file(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock, yaml_load: MagicMock):
    exists.return_value = True
    isfile.return_value = False
    yaml_load.return_value = {'key': 'value'}


    result = config_management.load_config()

    assert result == yaml_load.return_value
    makedirs.assert_not_called()
    assert open.call_count == 2


@patch.object(config_management, 'safe_print')
@patch.object(config_management, 'write_config')
@patch('yaml.safe_load')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_load_config_yaml_error(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock, yaml_load: MagicMock, write_config: MagicMock, safe_print: MagicMock):
    exists.return_value = True
    isfile.return_value = True
    yaml_load.side_effect = yaml.error.YAMLError()

    with pytest.raises(SystemExit):
        config_management.load_config()

    makedirs.assert_not_called()
    open.assert_called_once()


@patch.object(config_management, 'safe_print')
@patch('yaml.safe_dump')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_write_config(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock, yaml_dump: MagicMock, safe_print: MagicMock):
    exists.return_value = True
    isfile.return_value = True

    config_management.write_config({'key': 'value'})

    yaml_dump.assert_called_once_with({'key': 'value'}, open.return_value)
    makedirs.assert_not_called()
    open.assert_called_once()


@patch.object(config_management, 'safe_print')
@patch('yaml.safe_dump')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_write_config_no_path(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock, yaml_dump: MagicMock, safe_print: MagicMock):
    exists.return_value = False
    isfile.return_value = True

    config_management.write_config({'key': 'value'})

    yaml_dump.assert_called_once_with({'key': 'value'}, open.return_value)
    makedirs.assert_called_once()
    open.assert_called_once()


@patch.object(config_management, 'safe_print')
@patch('yaml.safe_dump')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_write_config_no_file(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock, yaml_dump: MagicMock, safe_print: MagicMock):
    exists.return_value = True
    isfile.return_value = False

    config_management.write_config({'key': 'value'})

    yaml_dump.assert_called_once_with({'key': 'value'}, open.return_value)
    makedirs.assert_not_called()
    assert open.call_count == 2


@patch.object(config_management, 'safe_print')
@patch('yaml.safe_dump')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_write_config_catches_exception(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock, yaml_dump: MagicMock, safe_print: MagicMock):
    exists.return_value = True
    isfile.return_value = False
    yaml_dump.side_effect = Exception()

    config_management.write_config({'key': 'value'})

    makedirs.assert_not_called()
    safe_print.assert_called()
    assert open.call_count == 2


@patch.object(config_management, 'safe_print')
@patch.object(config_management, 'load_config')
@patch.object(config_management, 'write_config')
def test_update_config_set(write_config: MagicMock, load_config: MagicMock, safe_print: MagicMock):
    load_config.return_value = {'key': 'value'}

    config_management.update_config(['set', 'x', 'y'])

    load_config.assert_called()
    write_config.assert_called_with({'key': 'value', 'x': 'y'})


@patch.object(config_management, 'defaults', {'key': 'default-value'})
@patch.object(config_management, 'safe_print')
@patch.object(config_management, 'load_config')
@patch.object(config_management, 'write_config')
def test_update_config_reset(write_config: MagicMock, load_config: MagicMock, safe_print: MagicMock):
    load_config.return_value = {'key': 'value'}

    config_management.update_config(['reset', 'key'])

    load_config.assert_called()
    write_config.assert_called_with({'key': 'default-value'})


@patch.object(config_management, 'defaults', {'key': 'default-value'})
@patch.object(config_management, 'safe_print')
@patch.object(config_management, 'load_config')
@patch.object(config_management, 'write_config')
def test_update_config_clear(write_config: MagicMock, load_config: MagicMock, safe_print: MagicMock):
    load_config.return_value = {'key': 'value'}

    config_management.update_config(['clear', 'key'])

    load_config.assert_called()
    write_config.assert_called_with({'key': 'default-value'})


@patch.object(config_management, 'defaults', {'key': 'default-value'})
@patch.object(config_management, 'safe_print')
@patch.object(config_management, 'load_config')
@patch.object(config_management, 'write_config')
def test_update_config_reset_no_key(write_config: MagicMock, load_config: MagicMock, safe_print: MagicMock):
    load_config.return_value = {'key': 'value'}

    config_management.update_config(['clear', 'no-key'])

    load_config.assert_called()
    write_config.assert_called_with({'key': 'value'})
    safe_print.assert_called_once()
