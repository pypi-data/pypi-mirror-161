# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['betting_models',
 'betting_models.core',
 'betting_models.football.league_markets',
 'betting_models.football.match_markets',
 'betting_models.generic',
 'betting_models.racing']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.2,<2.0.0',
 'pandas>=1.4.1,<2.0.0',
 'scipy>=1.8.0,<2.0.0',
 'seaborn>=0.11.2,<0.12.0']

setup_kwargs = {
    'name': 'betting-models',
    'version': '0.1.4',
    'description': 'Statistical tools for highly exotic betting markets.',
    'long_description': None,
    'author': 'Michael Watson',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<3.9.0',
}


setup(**setup_kwargs)
