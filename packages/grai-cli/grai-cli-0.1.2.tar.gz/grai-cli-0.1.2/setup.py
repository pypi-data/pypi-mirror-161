# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['grai_cli',
 'grai_cli.api',
 'grai_cli.api.config',
 'grai_cli.api.server',
 'grai_cli.settings',
 'grai_cli.utilities']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'apipkg>=3.0.1,<4.0.0',
 'click-spinner>=0.1.10,<0.2.0',
 'confuse>=1.7.0,<2.0.0',
 'fqdn>=1.5.1,<2.0.0',
 'grai-client>=0.1.3,<0.2.0',
 'multimethod>=1.8,<2.0',
 'pydantic>=1.9.1,<2.0.0',
 'requests>=2.28.1,<3.0.0',
 'rich>=12.5.1,<13.0.0',
 'tabulate>=0.8.10,<0.9.0',
 'tqdm>=4.64.0,<5.0.0',
 'typer>=0.6.1,<0.7.0',
 'validators>=0.20.0,<0.21.0']

entry_points = \
{'console_scripts': ['grai = grai_cli.api.entrypoint:app']}

setup_kwargs = {
    'name': 'grai-cli',
    'version': '0.1.2',
    'description': '',
    'long_description': '',
    'author': 'Ian Eaves',
    'author_email': 'ian@grai.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
