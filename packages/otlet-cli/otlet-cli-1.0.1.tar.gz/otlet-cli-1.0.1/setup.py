# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['otlet_cli', 'otlet_cli.clparser']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=1.2.2,<2.0.0', 'otlet>=1.0.0,<2.0.0']

entry_points = \
{'console_scripts': ['otlet = otlet_cli.cli:run_cli']}

setup_kwargs = {
    'name': 'otlet-cli',
    'version': '1.0.1',
    'description': 'CLI interface for otlet, the PyPI Web API wrapper',
    'long_description': '<div align="center">\n    <img src="https://commedesgarcons.s-ul.eu/zSyAjvoO" alt="otlet_cli readme image"><br>\n    CLI tool for querying the Python Packaging Index using <a href="https://github.com/nhtnr/otlet">Otlet</a>. \n\n[![license-mit](https://img.shields.io/pypi/l/otlet-cli)](https://github.com/nhtnr/otlet/blob/main/LICENSE)\n[![github-issues](https://img.shields.io/github/issues/nhtnr/otlet-cli)](https://github.com/nhtnr/otlet-cli/issues)\n[![github-pull-requests](https://img.shields.io/github/issues-pr/nhtnr/otlet-cli)](https://github.com/nhtnr/otlet-cli/pulls)\n![pypi-python-versions](https://img.shields.io/pypi/pyversions/otlet-cli)\n[![pypi-package-version](https://img.shields.io/pypi/v/otlet-cli)](https://pypi.org/project/otlet-cli/)\n\n</div>\n\n# Installing\nOtlet-cli can be installed from pip using the following command:  \n  \n```\npip install -U otlet-cli\n```  \n  \nTo install from source, please see the [INSTALLING](https://github.com/nhtnr/otlet-cli/INSTALLING.md) file.\n  \n# Usage\nGet info about a particular package:  \n  \n  ```\n  otlet sampleproject\n  ```  \n  \nOr a specific version:  \n  \n  ```\n  otlet django 4.0.6\n  ```  \n  \nCheck out all available releases for a package:  \n  \n  ```\n  otlet releases tensorflow\n  ```  \n\nList all available wheels:  \n  \n  ```\n  otlet download torch -l\n  ``` \n  \nThen download a wheel for Python 3.9 on x86_64 macOS:  \n  \n  ```\n  otlet download torch -w "python_tag:3.9,platform_tag:macosx*x86_64"\n  ```\n  \nAnd more... just run:  \n  \n  ```\n  otlet --help\n  ```  \n   \n# Contributing\nIf you notice any issues, or think a new feature would be nice, feel free to open an [issue](https://github.com/nhtnr/otlet-cli/issues).\n',
    'author': 'Noah Tanner (nhtnr)',
    'author_email': 'noahtnr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nhtnr/otlet-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
