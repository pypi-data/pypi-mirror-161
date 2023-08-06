"""
Global Filters
``````````````

The following are functions provided to Fyoo's jinja
runtime as jinja filters.
"""
import json

import yaml

__all__ = [
    'toJson',
    'toYaml',
]

toJson = json.dumps
"""Alias of json.dumps

.. code-block:: console

   $ fyoo -- echo "{{ [{'a': 1}, {'b': 2}] | toJson }}"
   [{"a": 1}, {"b": 2}]

"""
toYaml = yaml.safe_dump
"""Alias of yaml.safe_dump

.. code-block:: console

   $ fyoo -- echo "{{ [{'a': 1}, {'b': 2}] | toYaml }}"
   - a: 1
   - b: 2

"""
