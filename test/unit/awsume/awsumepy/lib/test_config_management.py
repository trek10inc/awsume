import pytest
from unittest.mock import patch, MagicMock

import yaml
from awsume.awsumepy.lib import config_management, exceptions


@patch('awsume.awsumepy.lib.constants.IS_USING_XDG_CONFIG_HOME', False)
@patch('yaml.safe_load')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_load_config(
        exists: MagicMock,
        isfile: MagicMock,
        makedirs: MagicMock,
        open: MagicMock,
        yaml_load: MagicMock,
):
    exists.return_value = True
    isfile.return_value = True
    yaml_load.return_value = {'key': 'value'}

    result = config_management.load_config()

    assert result == yaml_load.return_value
    makedirs.assert_not_called()

@patch('awsume.awsumepy.lib.constants.IS_USING_XDG_CONFIG_HOME', False)
@patch('yaml.safe_load')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_load_config_no_path(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock,
                             yaml_load: MagicMock):
    exists.return_value = False
    isfile.return_value = True
    yaml_load.return_value = {'key': 'value'}

    result = config_management.load_config()

    assert result == yaml_load.return_value
    makedirs.assert_called()
    open.assert_called_once()
    assert makedirs.call_count == 3

@patch('awsume.awsumepy.lib.constants.IS_USING_XDG_CONFIG_HOME', False)
@patch('yaml.safe_load')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_load_config_no_file(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock,
                             yaml_load: MagicMock):
    exists.return_value = True
    isfile.return_value = False
    yaml_load.return_value = {'key': 'value'}

    result = config_management.load_config()

    assert result == yaml_load.return_value
    makedirs.assert_not_called()
    assert open.call_count == 2

@patch('awsume.awsumepy.lib.constants.IS_USING_XDG_CONFIG_HOME', False)
@patch.object(config_management, 'safe_print')
@patch.object(config_management, 'write_config')
@patch('yaml.safe_load')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_load_config_yaml_error(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock,
                                yaml_load: MagicMock, write_config: MagicMock, safe_print: MagicMock):
    exists.return_value = True
    isfile.return_value = True
    yaml_load.side_effect = yaml.error.YAMLError()

    with pytest.raises(exceptions.ConfigParseException):
        config_management.load_config()

    makedirs.assert_not_called()
    open.assert_called_once()

@patch.object(config_management, 'safe_print')
@patch('yaml.safe_dump')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_write_config(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock, yaml_dump: MagicMock,
                      safe_print: MagicMock):
    exists.return_value = True
    isfile.return_value = True

    config_management.write_config({'key': 'value'})

    yaml_dump.assert_called_once_with({'key': 'value'}, open.return_value, width=1000)
    makedirs.assert_not_called()
    open.assert_called_once()


@patch.object(config_management, 'safe_print')
@patch('yaml.safe_dump')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_write_config_no_path(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock,
                              yaml_dump: MagicMock, safe_print: MagicMock):
    exists.return_value = False
    isfile.return_value = True

    config_management.write_config({'key': 'value'})

    yaml_dump.assert_called_once_with({'key': 'value'}, open.return_value, width=1000)
    makedirs.assert_called_once()
    open.assert_called_once()


@patch.object(config_management, 'safe_print')
@patch('yaml.safe_dump')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_write_config_no_file(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock,
                              yaml_dump: MagicMock, safe_print: MagicMock):
    exists.return_value = True
    isfile.return_value = False

    config_management.write_config({'key': 'value'})

    yaml_dump.assert_called_once_with({'key': 'value'}, open.return_value, width=1000)
    makedirs.assert_not_called()
    assert open.call_count == 2


@patch.object(config_management, 'safe_print')
@patch('yaml.safe_dump')
@patch('builtins.open')
@patch('os.makedirs')
@patch('os.path.isfile')
@patch('os.path.exists')
def test_write_config_catches_exception(exists: MagicMock, isfile: MagicMock, makedirs: MagicMock, open: MagicMock,
                                        yaml_dump: MagicMock, safe_print: MagicMock):
    exists.return_value = True
    isfile.return_value = False
    yaml_dump.side_effect = Exception()

    config_management.write_config({'key': 'value'})

    makedirs.assert_not_called()
    safe_print.assert_called()
    assert open.call_count == 2
