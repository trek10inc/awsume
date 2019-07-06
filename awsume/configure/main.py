import argparse, os, sys
from . import alias, autocomplete


def parse_args(argv: sys.argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--shell',
        dest='shell',
        metavar='shell',
        help='The shell you will use awsume under',
        required=True,
        choices=['bash', 'zsh', 'powershell']
    )
    parser.add_argument('--autocomplete-file',
        dest='autocomplete_file',
        metavar='autocomplete_file',
        required=True,
        help='The file you want the autocomplete script to be defined in',
    )
    parser.add_argument('--alias-file',
        default=None,
        dest='alias_file',
        metavar='alias_file',
        required=False,
        help='The file you want the alias to be defined in',
    )
    args = parser.parse_args(argv)

    if args.shell in ['powershell'] and args.alias_file:
        parser.error('No alias file is needed for shell: powershell')

    return args


def run(shell: str, alias_file: str, autocomplete_file: str):
    if alias_file:
        alias.main(shell, alias_file)
    if autocomplete_file:
        autocomplete.main(shell, autocomplete_file)


def main():
    args = parse_args(sys.argv[1:])
    run(args.shell, args.alias_file, args.autocomplete_file)
