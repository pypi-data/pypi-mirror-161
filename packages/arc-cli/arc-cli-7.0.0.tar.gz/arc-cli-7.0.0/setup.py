# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arc',
 'arc._command',
 'arc._command.param',
 'arc.present',
 'arc.prompt',
 'arc.types',
 'arc.types.middleware',
 'arc.types.transforms',
 'arc.types.validators']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'arc-cli',
    'version': '7.0.0',
    'description': 'A Regular CLI',
    'long_description': '# ARC: A Regular CLI\nA tool for building declartive, and highly extendable CLI systems for Python 3.9\n\n# ARC Features\n- Command line arguments based on python type hints\n- Arbitrary command nesting\n- Automatic `--help` documentation\n- Dynamic command loading at runtime\n\n# [Docs](http://arc.seanrcollings.com)\n\n# Quick Start\n\n```py\nimport arc\n\n@arc.command()\ndef hello(name: str):\n    """My first arc program!"""\n    arc.arc.print(f"Hello {name}!")\n\nhello()\n```\n\n```\n$ python hello.py Sean\nHello, Sean!\n```\n\n```\nUSAGE\n    hello.py [-h] [--] name\n\nDESCRIPTION\n    My first arc program!\n\nARGUMENTS\n    name\n\nOPTIONS\n    --help (-h)  Displays this help message\n```\n\n# Installation\n\n```\n$ pip install arc-cli\n```\n\nClone for development\n```\n$ git clone https://github.com/seanrcollings/arc\n$ poetry install\n```\n\n# Tests\nTests are written with `pytest`\n```\n$ pytest\n```\n\n# Attribution\nMuch of arc\'s architecture is based on [click](https://click.palletsprojects.com/en/8.0.x/), though no code is lifted directly from click\'s source.\n',
    'author': 'Sean Collings',
    'author_email': 'seanrcollings@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/seanrcollings/arc',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
