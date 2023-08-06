# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ocdc']

package_data = \
{'': ['*']}

install_requires = \
['packaging>=21.3,<22.0', 'pydantic>=1.9.1,<2.0.0']

entry_points = \
{'console_scripts': ['ocdc = ocdc.__main__:main']}

setup_kwargs = {
    'name': 'ocdc',
    'version': '0.3.0',
    'description': 'A changelog formatter for "people", neat freaks, and sloppy typists.',
    'long_description': '![OCDC Logo](/logo.png)\n\n<h2 align="center">Obsessive-Compulsive Development Changelogs</h2>\n\n`ocdc` is a changelog formatter for "people", neat freaks, and sloppy typists.\n\nThe format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\nwith some slight modifications:\n\n- Lines are wrapped at 90 characters.\n- Version sections are separated by two blank lines to aid visual scanning.\n- Square brackets are not used in titles. Changelogs aren\'t programming\n  languages, so why throw in weird symbols like that?\n\n\n## Installation\n\n```console\n$ pip install ocdc\n```\n\n\n## Usage\n\nTo format `CHANGELOG.md` in the current directory, run `ocdc` without arguments.\nYou can also pass a custom path.\n\n```console\n$ ocdc [--path CHANGELOG.md]\n```\n\nTo check `CHANGELOG.md` without modifying the file, use `--check`.\n\n```console\n$ ocdc --check [--path CHANGELOG.md]\n```\n\nTo create a new `CHANGELOG.md`, use the `new` subcommand.\n\n```console\n$ ocdc new [--force]\n```\n\nFor a description of all options, use `--help`.\n\n```console\n$ ocdc --help\n```\n\n\n## Configuration\n\nConfiguration is for the weak-willed. There shall be only one true format.\n\n\n## Disclaimer\n\nThis thing is new, and it might eat your changelog! Back up your files (in git)\nbefore trying `ocdc`.\n',
    'author': 'Matteo De Wint',
    'author_email': 'matteo@mailfence.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mdwint/ocdc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
