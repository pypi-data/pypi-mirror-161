# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['turba']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'beautifulsoup4>=4.9.3,<5.0.0',
 'bencode.py>=4.0.0,<5.0.0',
 'object-colors>=2.1.0,<3.0.0',
 'transmission-rpc>=3.2.1,<4.0.0']

entry_points = \
{'console_scripts': ['turba = turba.__main__:main']}

setup_kwargs = {
    'name': 'turba',
    'version': '0.1.0',
    'description': 'Turbocharged torrent scraper',
    'long_description': 'turba\n=====\n.. image:: https://img.shields.io/badge/License-MIT-yellow.svg\n    :target: https://opensource.org/licenses/MIT\n    :alt: License\n.. image:: https://img.shields.io/pypi/v/turba\n    :target: https://img.shields.io/pypi/v/turba\n    :alt: pypi\n.. image:: https://github.com/jshwi/turba/actions/workflows/ci.yml/badge.svg\n    :target: https://github.com/jshwi/turba/actions/workflows/ci.yml\n    :alt: CI\n.. image:: https://github.com/jshwi/turba/actions/workflows/codeql-analysis.yml/badge.svg\n    :target: https://github.com/jshwi/turba/actions/workflows/codeql-analysis.yml\n    :alt: CodeQL\n.. image:: https://codecov.io/gh/jshwi/turba/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/jshwi/turba\n    :alt: codecov.io\n.. image:: https://readthedocs.org/projects/turba/badge/?version=latest\n    :target: https://turba.readthedocs.io/en/latest/?badge=latest\n    :alt: readthedocs.org\n.. image:: https://img.shields.io/badge/python-3.8-blue.svg\n    :target: https://www.python.org/downloads/release/python-380\n    :alt: python3.8\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    :alt: black\n\nTurbocharged torrent scraper\n----------------------------\n\nRequires `transmission-daemon`\n\nUsage\n*****\n\n.. code-block:: console\n\n    usage: turba [-h] URL\n\n    positional arguments:\n      URL         url to harvest\n\n    optional arguments:\n      -h, --help  show this help message and exit\n',
    'author': 'jshwi',
    'author_email': 'stephen@jshwisolutions.com',
    'maintainer': 'jshwi',
    'maintainer_email': 'stephen@jshwisolutions.com',
    'url': 'https://pypi.org/project/turba/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
