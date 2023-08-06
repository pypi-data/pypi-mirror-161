"""
Global Attributes
`````````````````

The following attributes are provided to Fyoo's jinja
environment as globals, whether they are objects
or callable functions.

"""
import datetime
import os
import pytz

from fyoo.exception import FyooTemplateException


__all__ = [
    'raw_datetime',
    'date',
    'getenv',
    'throw',
]

raw_datetime = datetime.datetime


def date(tz='UTC', fmt: str = r'%Y-%m-%d') -> str:
    """Get current time string

    .. code-block:: console

       $ fyoo -- echo 'today is {{ date() }}'
       today is 2020-01-01

       $ fyoo -- echo 'the year is {{ date(fmt="%Y") }}'
       the year is 2020


    Args:
        tz (str, optional): Timezone to use. Defaults to 'UTC'.
        fmt (str, optional): Datetime format. Defaults to r'%Y-%m-%d'.

    Returns:
        str: Formated datetime string
    """
    return datetime.datetime.now(tz=pytz.timezone(tz)).strftime(fmt)

getenv = os.getenv
"""Alias of os.getenv

.. code-block:: console

   $ fyoo -- echo 'I am a {{ getenv("USER") }}'
   I am a coolcat
   $ fyoo -- echo 'example {{ getenv("IDONTEXIST", "default") }}'
   example default

"""

    # ""Alias of os.getenv

    # .. code-block:: console

    # $ fyoo -- echo 'I am a {{ getenv("USER") }}
    # I am a coolcat
    # $ fyoo -- echo 'example {{ getenv("IDONTEXIST", "default") }}'
    # example default

    # ""

def throw(*args):
    # pylint: disable=line-too-long
    """Raise a FyooTemplateException

    You would do this if you wanted to verify arguments
    at 'compile-time', before executing a subcommand.

    .. code-block:: console

       $ fyoo -- echo '{% if not table %}{{ throw("table not set") }}{% endif %}table is {{ table }}'
       fyoo.exception.FyooTemplateException: table not set

       $ fyoo --set table=customer -- echo '{% if not table %}{{ throw("table not set") }}{% endif %}table is {{ table }}'
       table is customer

    """
    raise FyooTemplateException(*args)
