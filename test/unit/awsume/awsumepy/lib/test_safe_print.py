import colorama
import os
from io import StringIO
from unittest.mock import patch, MagicMock

from awsume.awsumepy.lib.safe_print import safe_print


@patch('yaml.safe_load')
@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdout', new_callable=StringIO)
@patch.object(safe_print, 'open', create=True)
def test_safe_print(open: MagicMock, stdout: MagicMock, stderr: MagicMock, yaml_load: MagicMock):
    yaml_load.return_value = {'colors': True}
    with patch.object(os, 'name', 'darwin'):
        safe_print('Text')
    assert stdout.getvalue() == ''
    assert 'Text' in stderr.getvalue()


@patch('yaml.safe_load')
@patch('sys.stderr', new_callable=StringIO)
@patch.object(safe_print, 'open', create=True)
def test_safe_print_color(open: MagicMock, stderr: MagicMock, yaml_load: MagicMock):
    yaml_load.return_value = {'colors': True}
    with patch.object(os, 'name', 'nt'):
        safe_print('Text', color=colorama.Fore.RED)
    assert colorama.Fore.RED not in stderr.getvalue()
    with patch.object(os, 'name', 'darwin'):
        safe_print('Text', color=colorama.Fore.RED)
    assert colorama.Fore.RED in stderr.getvalue()


@patch('sys.stderr', new_callable=StringIO)
@patch.object(safe_print, 'open', create=True)
def test_safe_print_end(open: MagicMock, stderr: MagicMock):
    safe_print('Text', end='')
    assert '\n' not in stderr.getvalue()


@patch('os.name', 'nt')
@patch('sys.stderr', new_callable=StringIO)
@patch.object(safe_print, 'open', create=True)
def test_safe_print_ignore_color_on_windows(open: MagicMock, stderr: MagicMock):
    safe_print('Text', color=colorama.Fore.RED)
    assert colorama.Fore.RED not in stderr.getvalue()
