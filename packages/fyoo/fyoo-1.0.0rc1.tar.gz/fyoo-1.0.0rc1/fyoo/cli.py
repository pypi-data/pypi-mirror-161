import argparse
import json
import os
import shutil
import sys
from typing import Optional, List, Sequence, Text

from fyoo.parser import FyooParser


class CliSingleton:

    __instance = None

    DESCRIPTION = '''
    This utility wraps around a command, and templates in context to
    the latter command's arguments. The child process will replace
    the fyoo/python process.
    '''.strip()
    HELP = {
        'exec': '''
        Execute a subcommand. The subcommand will spawn a child process that
        will become a parent (implemented by ``os.execvp``).
        '''.strip(),
        'command': 'Enter any number of arguments as a command.',
        'dry_run': 'Do not actually kick off command.',
        'verbose': 'Show the command before running it.',
    }

    def __init__(self):
        _C = CliSingleton
        self.parser = FyooParser(
            'fyoo', description=_C.DESCRIPTION,
            formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, width=120))
        self.parser.add_argument('-v', '--verbose', action='store_true', default=False, help=_C.HELP['verbose'])
        self.parser.add_argument('-dr', '--dry-run', action='store_true', default=False, help=_C.HELP['dry_run'])
        subparsers = self.parser.add_subparsers(parser_class=argparse.ArgumentParser)
        subparsers.required = True
        exec_parser = subparsers.add_parser('--', help=_C.HELP['exec'])
        exec_parser.set_defaults(callback=self.exec)
        exec_parser.add_argument('command', nargs=argparse.REMAINDER, help=_C.HELP['command'])

    def exec(self, dry_run: bool, verbose: bool, command: List[str]):
        if dry_run or verbose:
            print(json.dumps(command))
        if not dry_run:
            if shutil.which(command[0]) is None:
                self.parser.error(f"Executable '{command[0]}' does not exist")
            os.execvp(command[0], command)

    def main(self, args: Sequence[Text]) -> None:
        try:
            arg_dict = vars(self.parser.parse_args(args))
        except TypeError as err:
            if err.args == ('sequence item 0: expected str instance, NoneType found', ):
                self.parser.error('Please provide a subcommand')
            raise

        callback = arg_dict.pop('callback')
        callback(**arg_dict)

    def __new__(cls, *args, **kwargs):
        if not kwargs.pop('_is_instance_call', False):
            raise ValueError("Can not instantiate, use .instance() instead")
        return super(CliSingleton, cls).__new__(cls, *args, **kwargs)

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = cls.__new__(cls, _is_instance_call=True)
            # pylint: disable=unnecessary-dunder-call
            cls.__instance.__init__()
        return cls.__instance

    @classmethod
    def remove(cls):
        if cls.__instance is not None:
            CliSingleton.__instance = None


def get_parser() -> FyooParser:
    return CliSingleton.instance().parser


def main(args: Optional[Sequence[Text]] = None):
    if args is None:
        args = sys.argv[1:]

    cli = CliSingleton.instance()

    cli.main(args)


if __name__ == '__main__':
    main()
