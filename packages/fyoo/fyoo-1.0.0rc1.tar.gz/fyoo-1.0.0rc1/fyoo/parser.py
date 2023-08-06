from argparse import ArgumentParser
import json
from typing import List, Optional, Tuple, Union
import os

import jinja2
import yaml

from .template import (
    filters as fyoo_filters,
    attributes as fyoo_attributes,
)

_FYOO_SET_PREFIX = 'FYOO__SET__'


def implicit_type(string: str) -> Union[bool, int, float, str]:
    if string.lower() in {'true', 'false'}:
        if string.lower() == 'true':
            return True
        return False
    try:
        return int(string)
    except ValueError:
        pass
    try:
        return float(string)
    except ValueError:
        pass
    return string


def _parse_template_context(context_format: str, context_string: str):
    parse_methods = {
        'json': json.loads,
        'yaml': yaml.safe_load,
    }
    if context_format in parse_methods:
        result = parse_methods[context_format](context_string)
        if isinstance(result, dict):
            return result
        raise ValueError(f"Context was not a dictionary with format '{context_format}'")
    raise ValueError(f"Unrecognized context format '{context_format}'")


def _generate_fyoo_context(
        context_format: str,
        context_strings: Optional[List[str]],
        additional_vars: Optional[List[Tuple[str, str]]],
) -> dict:
    result_template = {}

    for key in filter(lambda k: k.startswith(_FYOO_SET_PREFIX) and len(k) > len(_FYOO_SET_PREFIX), os.environ.keys()):
        result_template[key[len(_FYOO_SET_PREFIX):]] = implicit_type(os.environ[key])

    if context_strings:
        for context_string in context_strings:
            result_template.update(_parse_template_context(context_format, context_string))
    if additional_vars:
        for key, value in additional_vars:
            result_template[key] = implicit_type(value)
    return result_template


def _set_type(string) -> Tuple[str, str]:
    eq_index = string.index('=')
    return string[:eq_index], string[eq_index + 1:]


class _FyooSecretParser(ArgumentParser):

    def __init__(self, *args, parent_parser: Optional = None, **kwargs) -> None:
        if not parent_parser:
            raise ValueError("'parent_parser' not provided")
        self.parent_parser = parent_parser
        super().__init__(*args, add_help=False, **kwargs)

    def add_argument(self, *args, **kwargs):
        self.parent_parser.add_argument(*args, **kwargs)
        super().add_argument(*args, **kwargs)


class FyooParser(ArgumentParser):

    """
    Just like an ArgumentParser, but adds a few hidden arguments. These
    hidden arguments will not show up in returned namespaces, rather they
    will simply tweak the full namespace before it comes back.
    """

    HELP = {
        'context': '''
Pass in a json or yaml string (multi-argument).
Can be set a single time by FYOO__CONTEXT.
'''.strip(),
        'context_format': '''
Context formatter to use.
Can be set by environment variable FYOO__CONTEXT_FORMAT.
'''.strip(),
        'set': r'''
Set a single context variable, i.e. table_name=users.

In addition, set context variables by environment variable
FYOO__SET__{var_name}={var_value}.

Context variables will try to use implicit types, defaulting
to string types.
        '''.strip(),
        'jinja_extension': '''Add a jinja2 extension to load at runtime.
        Can be set by environment variable FYOO__JINJA_EXTENSION, where ':' separates multiple extensions.''',
        'jinja_template_folder': '''Optionally, add a location for jinja2 to load templates from the filesystem.
        Can be set by environment variable FYOO__JINJA_TEMPLATE_FOLDER.''',
        'jinja_block_string': '''Jinja block start and end strings for blocks. Can be set
        by environment variables FYOO__JINJA_BLOCK_STRING__S/E''',
        'jinja_variable_string': '''Jinja block start and end strings for variables. Can be set
        by environment variables FYOO__JINJA_VARIABLE_STRING__S/E''',
        'jinja_comment_string': '''Jinja block start and end strings for comments. Can be set
        by environment variables FYOO__JINJA_COMMENT_STRING__S/E''',
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        _F = FyooParser  # Short variable name for local access
        self.fyoo_secret_parser = _FyooSecretParser(parent_parser=self)
        self.fyoo_secret_parser.add_argument(
            '-c', '--context', action='append', help=_F.HELP['context'],
            default=[os.getenv('FYOO__CONTEXT')]
            if os.getenv('FYOO__CONTEXT')
            else [])
        self.fyoo_secret_parser.add_argument(
            '-f', '--context-format', help=_F.HELP['context_format'], default=os.getenv('FYOO__CONTEXT_FORMAT', 'json'))
        self.fyoo_secret_parser.add_argument(
            '-s', '--set', action='append', type=_set_type, help=_F.HELP['set'])
        self.fyoo_secret_parser.add_argument(
            '-je', '--jinja-extension', action='append', help=_F.HELP['jinja_extension'],
            default=[
                ext for ext in os.getenv('FYOO__JINJA_EXTENSION', '').split(':')
                if ext])
        self.fyoo_secret_parser.add_argument(
            '-jtf', '--jinja-template-folder', help=_F.HELP['jinja_template_folder'],
            default=os.getenv('FYOO__JINJA_TEMPLATE_FOLDER'))
        self.fyoo_secret_parser.add_argument(
            '-jbs', '--jinja-block-string', nargs=2, help=_F.HELP['jinja_block_string'],
            default=[os.getenv('FYOO__JINJA_BLOCK_STRING__S', '{%'),
                     os.getenv('FYOO__JINJA_BLOCK_STRING__E', '%}')])
        self.fyoo_secret_parser.add_argument(
            '-jvs', '--jinja-variable-string', nargs=2, help=_F.HELP['jinja_variable_string'],
            default=[os.getenv('FYOO__JINJA_VARIABLE_STRING__S', r'{{'),
                     os.getenv('FYOO__JINJA_VARIABLE_STRING__E', r'}}')])
        self.fyoo_secret_parser.add_argument(
            '-jcs', '--jinja-comment-string', nargs=2, help=_F.HELP['jinja_comment_string'],
            default=[os.getenv('FYOO__JINJA_COMMENT_STRING__S', '{#'),
                     os.getenv('FYOO__JINJA_COMMENT_STRING__E', '#}')])


    def parse_known_args(self, args=None, namespace=None):
        secret_known_args, secret_unknown_args = \
            self.fyoo_secret_parser.parse_known_args(args=args, namespace=namespace)

        loader = None \
                if secret_known_args.jinja_template_folder is None \
                else jinja2.FileSystemLoader(searchpath=secret_known_args.jinja_template_folder)
        jinja_env = jinja2.Environment(
            block_start_string=secret_known_args.jinja_block_string[0],
            block_end_string=secret_known_args.jinja_block_string[1],
            variable_start_string=secret_known_args.jinja_variable_string[0],
            variable_end_string=secret_known_args.jinja_variable_string[1],
            comment_start_string=secret_known_args.jinja_comment_string[0],
            comment_end_string=secret_known_args.jinja_comment_string[1],
            loader=loader,
        )

        jinja_env.globals.update({
            attr_name: getattr(fyoo_attributes, attr_name)
            for attr_name in fyoo_attributes.__all__
        })
        jinja_env.filters.update({
            attr_name: getattr(fyoo_filters, attr_name)
            for attr_name in fyoo_filters.__all__
        })

        if secret_known_args.jinja_extension:
            for fyoo_jinja_extension in secret_known_args.jinja_extension:
                jinja_env.add_extension(fyoo_jinja_extension)

        # Remove actions from current parser, as they're passed to fyoo inner secret-parser
        # pylint: disable=protected-access
        secret_action_dests = {action.dest for action in self.fyoo_secret_parser._actions}
        for action in list(self._actions):  # Need list to remove unstable iterable
            if action.dest in secret_action_dests:
                self._remove_action(action)

        template_context = _generate_fyoo_context(
            secret_known_args.context_format,
            secret_known_args.context,
            secret_known_args.set,
        )
        jinja_env.globals.update(template_context)

        known_args, unknown_args = super().parse_known_args(
            # Only use args that secret parser did not parse
            args=[
                jinja_env.from_string(arg).render()
                for arg in secret_unknown_args
            ],
            # But use initial optional namespace object
            namespace=namespace,
        )

        return known_args, unknown_args
