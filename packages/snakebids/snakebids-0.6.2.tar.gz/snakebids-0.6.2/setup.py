# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snakebids',
 'snakebids.core',
 'snakebids.project_template.{{cookiecutter.app_name}}',
 'snakebids.project_template.{{cookiecutter.app_name}}.docs',
 'snakebids.project_template.{{cookiecutter.app_name}}.{{cookiecutter.app_name}}',
 'snakebids.resources',
 'snakebids.utils']

package_data = \
{'': ['*'],
 'snakebids': ['project_template/*'],
 'snakebids.project_template.{{cookiecutter.app_name}}': ['config/*',
                                                          'workflow/*'],
 'snakebids.project_template.{{cookiecutter.app_name}}.docs': ['getting_started/*',
                                                               'usage/*']}

install_requires = \
['PyYAML>=6,<7',
 'attrs>=21.2.0,<22.0.0',
 'boutiques>=0.5.25,<0.6.0',
 'cached-property>=1.5.2,<2.0.0',
 'colorama>=0.4.4,<0.5.0',
 'cookiecutter>=2.1.1,<3.0.0',
 'more-itertools>=8.12.0,<9.0.0',
 'pybids>=0.15.0,<0.16.0',
 'snakemake>=5.28.0',
 'typing-extensions>=3.10.0,<4.0.0']

entry_points = \
{'console_scripts': ['snakebids = snakebids.admin:main']}

setup_kwargs = {
    'name': 'snakebids',
    'version': '0.6.2',
    'description': 'BIDS integration into snakemake workflows',
    'long_description': "\nsnakebids\n=========\n[![Tests](https://github.com/akhanf/snakebids/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/akhanf/snakebids/actions/workflows/test.yml?query=branch%3Amain)\n[![Documentation Status](https://readthedocs.org/projects/snakebids/badge/?version=stable)](https://snakebids.readthedocs.io/en/stable/?badge=stable)\n[![Version](https://img.shields.io/github/v/tag/akhanf/snakebids?label=version)](https://pypi.org/project/snakebids/)\n[![Python versions](https://img.shields.io/pypi/pyversions/snakebids)](https://pypi.org/project/snakebids/)\n[![DOI](https://zenodo.org/badge/309495236.svg)](https://zenodo.org/badge/latestdoi/309495236)\n\nSnakemake + BIDS\nThis package allows you to build BIDS Apps using Snakemake. It offers:\n\n\n* Flexible data grabbing with PyBIDS, configurable solely by config file entries\n* Helper function for creating BIDS paths inside Snakemake workflows/rules\n* Command-line invocation of snakemake workflows with BIDS App compliance\n* Configurable argument parsing specified using the Snakemake workflow config\n* Execution either as command-line BIDS apps or via snakemake executable\n\nContributing\n============\n\nClone the git repository. Snakebids dependencies are managed with Poetry, which you'll need installed on your machine. You can find instructions on the [poetry website](https://python-poetry.org/docs/master/#installation). Then, setup the development environment with the following commands:\n\n```bash\npoetry install\npoetry run poe setup\n```\n\nSnakebids uses [poethepoet](https://github.com/nat-n/poethepoet) as a task runner. You can see what commands are available by running:\n\n```bash\npoetry run poe\n```\n\nIf you wish, you can also run `poe [command]` directly by installing `poethepoet` on your system. Follow the install instructions at the link above.\n\nTests are done with `pytest` and can be run via:\n\n```bash\npoetry run pytest\n```\n\nSnakebids uses pre-commit hooks (installed via the `poe setup` command above) to lint and format code (we use [black](https://github.com/psf/black), [isort](https://github.com/PyCQA/isort), [pylint](https://pylint.org/) and [flake8](https://flake8.pycqa.org/en/latest/)). By default, these hooks are run on every commit. Please be sure they all pass before making a PR.\n",
    'author': 'Ali Khan',
    'author_email': 'alik@robarts.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/akhanf/snakebids',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
