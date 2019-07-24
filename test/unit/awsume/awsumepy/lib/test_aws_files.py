import os
import json
import pytest
import argparse
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from awsume.awsumepy.lib import constants
from awsume.awsumepy.lib import aws_files


def test_get_aws_files():
    args = argparse.Namespace(config_file=None, credentials_file=None)
    config = {}

    config_file, credentials_file = aws_files.get_aws_files(args, config)

    assert config_file == str(Path(constants.DEFAULT_CONFIG_FILE))
    assert credentials_file == str(Path(constants.DEFAULT_CREDENTIALS_FILE))


def test_get_aws_files_args():
    args = argparse.Namespace(config_file='my/config/file', credentials_file='my/credentials/file')
    config = {}

    config_file, credentials_file = aws_files.get_aws_files(args, config)

    assert config_file == str(Path('my/config/file'))
    assert credentials_file == str(Path('my/credentials/file'))



def test_get_aws_files_config():
    args = argparse.Namespace(config_file=None, credentials_file=None)
    config = {
        'config-file': 'my/config/file',
        'credentials-file': 'my/credentials/file',
    }

    config_file, credentials_file = aws_files.get_aws_files(args, config)

    assert config_file == str(Path('my/config/file'))
    assert credentials_file == str(Path('my/credentials/file'))


@patch.dict('os.environ', {'AWS_CONFIG_FILE': 'my/config/file', 'AWS_SHARED_CREDENTIALS_FILE': 'my/credentials/file'}, clear=True)
def test_get_aws_files_environment():
    args = argparse.Namespace(config_file=None, credentials_file=None)
    config = {}

    config_file, credentials_file = aws_files.get_aws_files(args, config)

    assert config_file == str(Path('my/config/file'))
    assert credentials_file == str(Path('my/credentials/file'))


@patch('builtins.open')
@patch('configparser.ConfigParser')
def test_add_section(ConfigParser: MagicMock, open: MagicMock):
    parser = MagicMock()
    ConfigParser.return_value = parser
    parser.has_section.return_value = True

    aws_files.add_section('section-name', {'key': 'value', 'key2': 'value2'}, 'file-name', overwrite=True)

    parser.read.assert_called_once_with('file-name')
    parser.remove_section.assert_called_once_with('section-name')
    parser.add_section.assert_called_once_with('section-name')
    assert parser.set.call_count == 2
    parser.write.assert_called_once()
    open.assert_called_once()


@patch.object(aws_files, 'safe_print')
@patch('builtins.open')
@patch('configparser.ConfigParser')
def test_add_section_no_overwrite(ConfigParser: MagicMock, open: MagicMock, safe_print: MagicMock):
    parser = MagicMock()
    ConfigParser.return_value = parser
    parser.has_section.return_value = True

    aws_files.add_section('section-name', {'key': 'value', 'key2': 'value2'}, 'file-name', overwrite=False)

    parser.read.assert_called_once_with('file-name')
    parser.remove_section.assert_not_called()
    parser.add_section.assert_not_called()
    parser.set.assert_not_called()



@patch.object(aws_files, 'safe_print')
@patch('builtins.open')
@patch('configparser.ConfigParser')
def test_add_section_new_section(ConfigParser: MagicMock, open: MagicMock, safe_print: MagicMock):
    parser = MagicMock()
    ConfigParser.return_value = parser
    parser.has_section.return_value = False

    aws_files.add_section('section-name', {'key': 'value', 'key2': 'value2'}, 'file-name')

    parser.read.assert_called_once_with('file-name')
    parser.remove_section.assert_not_called()
    parser.add_section.assert_called_once_with('section-name')
    assert parser.set.call_count == 2
    parser.write.assert_called_once()
    open.assert_called_once()


@patch('builtins.open')
@patch('configparser.ConfigParser')
def test_delete_section(ConfigParser: MagicMock, open: MagicMock):
    parser = MagicMock()
    ConfigParser.return_value = parser
    parser.has_section.return_value = True

    aws_files.delete_section('section-name', 'file-name')

    parser.read.assert_called_once_with('file-name')
    parser.remove_section.assert_called_once_with('section-name')
    parser.write.assert_called_once()
    open.assert_called_once()


@patch('builtins.open')
@patch('configparser.ConfigParser')
def test_delete_section_no_section(ConfigParser: MagicMock, open: MagicMock):
    parser = MagicMock()
    ConfigParser.return_value = parser
    parser.has_section.return_value = False

    aws_files.delete_section('section-name', 'file-name')

    parser.read.assert_called_once_with('file-name')
    parser.remove_section.assert_not_called()


myfile = """
[default]
region = us-east-1
mfa_serial = arn:aws:iam::123123123123:mfa/admin
"""
@patch('builtins.open')
def test_read_aws_file(open: MagicMock):
    open.return_value = StringIO(myfile)
    result = aws_files.read_aws_file('my/file/')
    assert result == {
        'default': {
            'region': 'us-east-1',
            'mfa_serial': 'arn:aws:iam::123123123123:mfa/admin',
        },
    }
